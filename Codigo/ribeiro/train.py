from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import (ModelCheckpoint, TensorBoard, ReduceLROnPlateau,
                                        CSVLogger, EarlyStopping)
import tensorflow as tf
from model import get_model
import argparse
from datasets import ECGSequence

if __name__ == "__main__":
    # Get data and train
    parser = argparse.ArgumentParser(description='Train neural network.')
    parser.add_argument('path_to_hdf5_train', type=str,
                        help='path to hdf5 file containing train tracings')
    parser.add_argument('path_to_hdf5_val', type=str,
                        help='path to hdf5 file containing validation tracings')
    parser.add_argument('path_to_csv_train', type=str,
                        help='path to csv file containing train annotations')
    parser.add_argument('path_to_csv_val', type=str,
                        help='path to csv file containing validation annotations')
   
    parser.add_argument('--dataset_name', type=str, default='tracings',
                        help='name of the hdf5 dataset containing tracings')
    args = parser.parse_args()

    #Train with multiple GPUs
    strategy = tf.distribute.MirroredStrategy()
    print('Number of devices: {}'.format(strategy.num_replicas_in_sync))

    with strategy.scope():
        # Optimization settings
        loss = 'binary_crossentropy'
        lr = 0.001
        batch_size = 64
        opt = Adam(lr)
        callbacks = [ReduceLROnPlateau(monitor='val_loss',
                                    factor=0.1,
                                    patience=7,
                                    min_lr=lr / 100),
                    EarlyStopping(patience=9,  # Patience should be larger than the one in ReduceLROnPlateau
                                min_delta=0.00001)]

        train_seq, valid_seq = ECGSequence.get_train_and_val(
            args.path_to_hdf5_train, args.path_to_hdf5_val, args.dataset_name, args.path_to_csv_train, args.path_to_csv_val, batch_size)

        # If you are continuing an interrupted section, uncomment line bellow:
        #   model = keras.models.load_model(PATH_TO_PREV_MODEL, compile=False)
        #Comprobamos la forma del primer valor de train_seq, y ese es el shape que le pasamos a get_model
        shape = train_seq.__getitem__(0)[0].shape[1:]
        model = get_model(train_seq.n_classes, shape=shape)
        model.compile(loss=loss, optimizer=opt)
        # Create log
        callbacks += [TensorBoard(log_dir='./logs', write_graph=False),
                    CSVLogger('training.log', append=False)]  # Change append to true if continuing training
        # Save the BEST and LAST model
        callbacks += [ModelCheckpoint('./backup_model_last.hdf5'),
                    ModelCheckpoint('./backup_model_best.hdf5', save_best_only=True)]
        # Train neural network
        history = model.fit(train_seq,
                            epochs=70,
                            initial_epoch=0,  # If you are continuing a interrupted section change here
                            callbacks=callbacks,
                            validation_data=valid_seq,
                            verbose=1)
        # Save final result
        model.save("./final_model.hdf5")