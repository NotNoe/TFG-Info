import pandas as pd
import numpy as np
import os
from sklearn.metrics import (confusion_matrix,
                             precision_score, recall_score, f1_score,
                             precision_recall_curve, average_precision_score)
import matplotlib.pyplot as plt
import seaborn as sns
import xarray as xr
from scipy.stats.distributions import chi2
from itertools import combinations

# %% Process arguments
import argparse
# %% Auxiliar functions
# check for --thresholds argument
parser = argparse.ArgumentParser()
parser.add_argument('prediction_file', type=str, default='./predictions.npy',)
parser.add_argument('path_to_csv', type=str, default='./y_test_ptb.csv',
                    help='path to csv file containing y_true')
parser.add_argument('--thresholds', type = str, default = None)
parser.add_argument('--is_superset', action='store_true', default=False)
args = parser.parse_args()
# In[23]:


def get_scores(y_true, y_pred, score_fun):
    nclasses = np.shape(y_true)[1]
    scores = []
    for name, fun in score_fun.items():
        scores += [[fun(y_true[:, k], y_pred[:, k]) for k in range(nclasses)]]
    return np.array(scores).T


# In[24]:


def specificity_score(y_true, y_pred):
    m = confusion_matrix(y_true, y_pred, labels=[0, 1])
    spc = m[0, 0] * 1.0 / (m[0, 0] + m[0, 1])
    return spc


# In[25]:


def get_optimal_precision_recall(y_true, y_score):
    """Find precision and recall values that maximize f1 score."""
    n = np.shape(y_true)[1]
    opt_precision = []
    opt_recall = []
    opt_threshold = []
    for k in range(n):
        # Get precision-recall curve
        precision, recall, threshold = precision_recall_curve(y_true[:, k], y_score[:, k])
        # Compute f1 score for each point (use nan_to_num to avoid nans messing up the results)
        f1_score = np.nan_to_num(2 * precision * recall / (precision + recall))
        # Select threshold that maximize f1 score
        index = np.argmax(f1_score)
        opt_precision.append(precision[index])
        opt_recall.append(recall[index])
        t = threshold[index-1] if index != 0 else threshold[0]-1e-10
        opt_threshold.append(t)
    return np.array(opt_precision), np.array(opt_recall), np.array(opt_threshold)

def get_precision_recall_for_threshold(y_true, y_pred, threshold):
    """Find precision and recall values for given threshold.
       Threshold is an array with the threshold for each class.
    """
    n = np.shape(y_true)[1]
    opt_precision = []
    opt_recall = []
    for k in range(n):
        # Get precision-recall curve
        precision, recall, threshold = precision_recall_curve(y_true[:, k], y_pred[:, k])
        # Select threshold that is closest to the given threshold
        index = np.argmin(np.abs(threshold - threshold[k]))
        opt_precision.append(precision[index])
        opt_recall.append(recall[index])
    return np.array(opt_precision), np.array(opt_recall), np.array(threshold)




# In[26]:


def affer_results(y_true, y_pred):
    """Return true positives, false positives, true negatives, false negatives.
    Parameters
    ----------
    y_true : ndarray
        True value
    y_pred : ndarray
        Predicted value
    Returns
    -------
    tn, tp, fn, fp: ndarray
        Boolean matrices containing true negatives, true positives, false negatives and false positives.
    cm : ndarray
        Matrix containing: 0 - true negative, 1 - true positive,
        2 - false negative, and 3 - false positive.
    """

    # True negative
    tn = (y_true == y_pred) & (y_pred == 0)
    # True positive
    tp = (y_true == y_pred) & (y_pred == 1)
    # False positive
    fp = (y_true != y_pred) & (y_pred == 1)
    # False negative
    fn = (y_true != y_pred) & (y_pred == 0)

    # Generate matrix of "tp, fp, tn, fn"
    m, n = np.shape(y_true)
    cm = np.zeros((m, n), dtype=int)
    cm[tn] = 0
    cm[tp] = 1
    cm[fn] = 2
    cm[fp] = 3
    return tn, tp, fn, fp, cm


# %% Constants

# In[27]:


score_fun = {'Precision': precision_score,
             'Recall': recall_score, 'Specificity': specificity_score,
             'F1 score': f1_score}
if args.is_superset:
    diagnosis = ['NORM', 'MI', 'STTC', 'CD', 'HYP', 'AF', 'PAC', 'PVC']
else:
    diagnosis = ['NORM', 'MI', 'STTC', 'CD', 'HYP']
nclasses = len(diagnosis)
predictor_names = ['DNN']


# %% Read datasets<br>
# Get true values

# In[28]:


# y_true = pd.read_csv('./Y-test-ptb-s.csv').values
y_true = pd.read_csv(args.path_to_csv).values
# y_true = pd.read_csv('./y_test_ptb.csv').values
# get y_score for model, output saved to dnn_output.npy
# y_pred = np.load('./predictions.npy')
y_pred = np.load(args.prediction_file)
# %% Get average model model<br>
# Get micro average precision

# In[29]:
np.shape(y_true)[1]
# In[30]:

if args.thresholds:
    thresh = np.loadtxt(args.thresholds)
    micro_avg_precision = average_precision_score(y_true, y_pred, average='micro')
    print('Micro average precision')
    print(micro_avg_precision)
    np.savetxt('./outputs/tables/micro_avg_precision.txt', [micro_avg_precision], fmt='%.3f')
    # get precision and recall for each class
    pre, rec, _ = get_precision_recall_for_threshold(y_true, y_pred, thresh)
else:
    micro_avg_precision = average_precision_score(y_true, y_pred, average='micro')
    print('Micro average precision')
    print(micro_avg_precision)
    # Get threshold that yield the best precision recall using "get_optimal_precision_recall" on validation set
    #   (we rounded it up to three decimal cases to make it easier to read...)
    pre, rec, thresh = get_optimal_precision_recall(y_true, y_pred)
    print('Optimal precision')
    print(pre)
    print('Optimal recall')
    print(rec)
    print('Optimal threshold')
    print(thresh)

    #Save micro average precision, optimal precision, recall and threshold to a file
    np.savetxt('./outputs/tables/micro_avg_precision.txt', [micro_avg_precision], fmt='%.3f')
    np.savetxt('./outputs/tables/optimal_precision.txt', pre, fmt='%.3f')
    np.savetxt('./outputs/tables/optimal_recall.txt', rec, fmt='%.3f')
    np.savetxt('./outputs/tables/optimal_threshold.txt', thresh, fmt='%.3f')
# In[ ]:





# In[31]:
# Get threshold that yield the best precision recall using "get_optimal_precision_recall" on validation set
#   (we rounded it up to three decimal cases to make it easier to read...)
mask = y_pred > thresh
# Get neural network prediction
# This data was also saved in './data/annotations/dnn.csv'
y_neuralnet = np.zeros_like(y_pred)
y_neuralnet[mask] = 1
y_neuralnet[mask] = 1


# %% Generate table with scores for the average model (Table 2)

# In[52]:


scores_list = []
for y_pred in [y_neuralnet]:
    # Compute scores
    scores = get_scores(y_true, y_pred, score_fun)
    # Put them into a data frame
    scores_df = pd.DataFrame(scores, index=diagnosis, columns=score_fun.keys())
    # Append
    scores_list.append(scores_df)
# Concatenate dataframes
scores_all_df = pd.concat(scores_list, axis=1, keys=['DNN'])
# Change multiindex levels
scores_all_df = scores_all_df.swaplevel(0, 1, axis=1)
scores_all_df = scores_all_df.reindex(level=0, columns=score_fun.keys())
# Save results
scores_all_df.to_excel("./outputs/tables/scores.xlsx", float_format='%.3f')
scores_all_df.to_csv("./outputs/tables/scores.csv", float_format='%.3f')


# In[51]:


# Compute scores
scores = get_scores(y_true, y_pred, score_fun)
# Put them into a data frame
scores_df = pd.DataFrame(scores, index=diagnosis, columns=score_fun.keys())
# Change multiindex levels
scores_all_df = scores_all_df.swaplevel(0, 1, axis=1)
scores_all_df = scores_all_df.reindex(level=0, columns=score_fun.keys())
# Save results
scores_all_df.to_excel("./outputs/tables/scores.xlsx", float_format='%.3f')
scores_all_df.to_csv("./outputs/tables/scores.csv", float_format='%.3f')


# %% Plot precision recall curves (Figure 2)

# In[33]:


for k, name in enumerate(diagnosis):
    precision_list = []
    recall_list = []
    threshold_list = []
    average_precision_list = []
    fig, ax = plt.subplots()
    lw = 2
    t = ['bo', 'rv', 'gs', 'kd']
    # Get precision-recall curve
    precision, recall, threshold = precision_recall_curve(y_true[:, k], y_pred[:, k])
    recall[np.isnan(recall)] = 0  # change nans to 0
    precision[np.isnan(precision)] = 0  # change nans to 0
    # Plot if is the choosen option
    ax.plot(recall, precision, color='blue', alpha=0.7)
    # Compute average precision
    average_precision = average_precision_score(y_true[:, k], y_pred[:, k])
    precision_list += [precision]
    recall_list += [recall]
    average_precision_list += [average_precision]
    threshold_list += [threshold]
    # Plot shaded region containing maximum and minimun from other executions
    recall_all = np.concatenate(recall_list)
    recall_all = np.sort(recall_all)  # sort
    recall_all = np.unique(recall_all)  # remove repeated entries
    recall_vec = []
    precision_min = []
    precision_max = []
    for r in recall_all:
        p_max = [max(precision[recall == r]) for recall, precision in zip(recall_list, precision_list)]
        p_min = [min(precision[recall == r]) for recall, precision in zip(recall_list, precision_list)]
        recall_vec += [r, r]
        precision_min += [min(p_max), min(p_min)]
        precision_max += [max(p_max), max(p_min)]
    ax.plot(recall_vec, precision_min, color='blue', alpha=0.3)
    ax.plot(recall_vec, precision_max, color='blue', alpha=0.3)
    ax.fill_between(recall_vec, precision_min, precision_max,
                    facecolor="blue", alpha=0.3)
    # Plot iso-f1 curves
    f_scores = np.linspace(0.1, 0.95, num=15)
    for f_score in f_scores:
        x = np.linspace(0.0000001, 1, 1000)
        y = f_score * x / (2 * x - f_score)
        ax.plot(x[y >= 0], y[y >= 0], color='gray', ls=':', lw=0.7, alpha=0.25)
    # Plot values in
    for npred in range(len(predictor_names)):
        ax.plot(scores_list[npred]['Recall'][k], scores_list[npred]['Precision'][k],
                t[npred], label=predictor_names[npred])
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.02])
    if k in [3, 4, 5]:
        ax.set_xlabel('Recall (Sensitivity)', fontsize=17)
    if k in [0, 3]:
        ax.set_ylabel('Precision (PPV)', fontsize=17)
    # plt.title('Precision-Recall curve (' + name + ')')
    if k == 0:
        plt.legend(loc="lower left", fontsize=17)
    else:
        ax.legend().remove()
    plt.tight_layout()
    plt.savefig('./outputs/figures/precision_recall_{0}.pdf'.format(name))


# %% Confusion matrices (Supplementary Table 1)

# In[34]:


M = [[confusion_matrix(y_true[:, k], y_pred[:, k], labels=[0, 1])
      for k in range(nclasses)] for y_pred in [y_neuralnet]]


# In[35]:


M_xarray = xr.DataArray(np.array(M),
                        dims=['predictor', 'diagnosis', 'true label', 'predicted label'],
                        coords={'predictor': ['DNN'],
                                'diagnosis': diagnosis,
                                'true label': ['not present', 'present'],
                                'predicted label': ['not present', 'present']})
confusion_matrices = M_xarray.to_dataframe('n')
confusion_matrices = confusion_matrices.reorder_levels([1, 2, 3, 0], axis=0)
confusion_matrices = confusion_matrices.unstack()
confusion_matrices = confusion_matrices.unstack()
confusion_matrices = confusion_matrices['n']
confusion_matrices.to_excel("./outputs/tables/confusion matrices.xlsx", float_format='%.3f')
confusion_matrices.to_csv("./outputs/tables/confusion matrices.csv", float_format='%.3f')


# % Compute scores and bootstraped version of these scores

# In[36]:


bootstrap_nsamples = 1000
percentiles = [2.5, 97.5]
scores_resampled_list = []
scores_percentiles_list = []
for y_pred in [y_neuralnet]:
    # Compute bootstraped samples
    np.random.seed(123)  # NEVER change this =P
    n, _ = np.shape(y_true)
    samples = np.random.randint(n, size=n * bootstrap_nsamples)
    # Get samples
    y_true_resampled = np.reshape(y_true[samples, :], (bootstrap_nsamples, n, nclasses))
    y_doctors_resampled = np.reshape(y_pred[samples, :], (bootstrap_nsamples, n, nclasses))
    # Apply functions
    scores_resampled = np.array([get_scores(y_true_resampled[i, :, :], y_doctors_resampled[i, :, :], score_fun)
                                 for i in range(bootstrap_nsamples)])
    # Sort scores
    scores_resampled.sort(axis=0)
    # Append
    scores_resampled_list.append(scores_resampled)

    # Compute percentiles index
    i = [int(p / 100.0 * bootstrap_nsamples) for p in percentiles]
    # Get percentiles
    scores_percentiles = scores_resampled[i, :, :]
    # Convert percentiles to a dataframe
    scores_percentiles_df = pd.concat([pd.DataFrame(x, index=diagnosis, columns=score_fun.keys())
                                       for x in scores_percentiles], keys=['p1', 'p2'], axis=1)
    # Change multiindex levels
    scores_percentiles_df = scores_percentiles_df.swaplevel(0, 1, axis=1)
    scores_percentiles_df = scores_percentiles_df.reindex(level=0, columns=score_fun.keys())
    # Append
    scores_percentiles_list.append(scores_percentiles_df)
# Concatenate dataframes
scores_percentiles_all_df = pd.concat(scores_percentiles_list, axis=1, keys=predictor_names)
# Change multiindex levels
scores_percentiles_all_df = scores_percentiles_all_df.reorder_levels([1, 0, 2], axis=1)
scores_percentiles_all_df = scores_percentiles_all_df.reindex(level=0, columns=score_fun.keys())


# % Print box plot (Supplementary Figure 1)<br>
# Convert to xarray

# In[37]:


scores_resampled_xr = xr.DataArray(np.array(scores_resampled_list),
                                   dims=['predictor', 'n', 'diagnosis', 'score_fun'],
                                   coords={
                                    'predictor': predictor_names,
                                    'n': range(bootstrap_nsamples),
                                    'diagnosis': diagnosis,
                                    'score_fun': list(score_fun.keys())})
# Remove everything except f1_score
for sf in score_fun:
    fig, ax = plt.subplots()
    f1_score_resampled_xr = scores_resampled_xr.sel(score_fun=sf)
    # Convert to dataframe
    f1_score_resampled_df = f1_score_resampled_xr.to_dataframe(name=sf).reset_index(level=[0, 1, 2])
    # Plot seaborn
    ax = sns.boxplot(x="diagnosis", y=sf, hue="predictor", data=f1_score_resampled_df)
    # Save results
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.xlabel("")
    plt.ylabel("", fontsize=16)
    if sf == "F1 score":
        plt.legend(fontsize=17)
    else:
        ax.legend().remove()
    plt.tight_layout()
    plt.savefig('./outputs/figures/boxplot_bootstrap_{}.pdf'.format(sf))


# In[38]:


scores_resampled_xr.to_dataframe(name='score').to_csv('./outputs/figures/boxplot_bootstrap_data.txt')


# % McNemar test  (Supplementary Table 3)<br>
# Get correct and wrong predictions for each of them (cm >= 2 correspond to wrong predictions)

# Nosotros no utilizamos porque no tenemos con que comprar ya que solo tenemos un modelo por ahora

# In[39]:


# wrong_predictions = np.array([affer_results(y_true, y_pred)[4] >= 2
#                               for y_pred in [y_neuralnet]])


# Compute McNemar score

# In[40]:


# names = ["DNN"]
# mcnemar_name = []
# mcnemar_score = np.empty((6, 6))
# k = 0
# for i in range(4):
#     for j in range(i+1, 4):
#         a_not_b = np.sum(wrong_predictions[i, :, :] & ~wrong_predictions[j, :, :], axis=0)
#         b_not_a = np.sum(~wrong_predictions[i, :, :] & wrong_predictions[j, :, :], axis=0)
#         # An alterantive to the standard McNemar test is to include a
#         # continuity correction term, resulting in:
#         # mcnemar_corr_score = np.square(np.abs(a_not_b - b_not_a) - 1) / (a_not_b + b_not_a)
#         # I tested both and came the conclusion, that we cannot reject the null hypotesis
#         # for neither. The standard test however provide results that are easier to visualize.
#         mcnemar_score[k, :] = np.square(a_not_b - b_not_a) / (a_not_b + b_not_a)
#         k += 1
#         mcnemar_name += [names[i] + " vs " + names[j]]


# In[41]:


# mcnemar = pd.DataFrame(1-chi2.cdf(mcnemar_score, 1), index=mcnemar_name, columns=diagnosis) # p-value


# Save results

# In[42]:


# mcnemar.to_excel("./outputs/tables/mcnemar.xlsx", float_format='%.3f')
# mcnemar.to_csv("./outputs/tables/mcnemar.csv", float_format='%.3f')


# %% Kappa score classifiers (Supplementary Table 2(a))

# In[43]:


# names = ["DNN", "cardio.", "emerg.", "stud."]
# predictors = [y_neuralnet, y_cardio, y_emerg, y_student]
# kappa_name = []
# kappa_score = np.empty((6, 6))
# k = 0
# for i in range(4):
#     for j in range(i+1, 4):
#         y_pred_1 = predictors[i]
#         y_pred_2 = predictors[j]
#         # Get "confusion matrix"
#         negative_negative, positive_positive, positive_negative, negative_positive, _ = \
#             affer_results(y_pred_1, y_pred_2)
#         p_p = positive_positive.sum(axis=0)
#         p_n = positive_negative.sum(axis=0)
#         n_p = negative_positive.sum(axis=0)
#         n_n = negative_negative.sum(axis=0)
#         total_sum = p_p + p_n + n_p + n_n
#         # Relative agreement
#         r_agree = (p_p + n_n) / total_sum
#         # Empirical probability of both saying yes
#         p_yes = (p_p + p_n) * (p_p + n_p) / total_sum**2
#         # Empirical probability of both saying no
#         p_no = (n_n + n_p) * (n_n + p_n) / total_sum**2
#         # Empirical probability of agreement
#         p_agree = p_yes + p_no
#         # Kappa score
#         kappa_score[k, :] = (r_agree - p_agree) / (1 - p_agree)
#         k += 1
#         kappa_name += [names[i] + " vs " + names[j]]


# In[44]:


# kappa = pd.DataFrame(kappa_score, index=kappa_name, columns=diagnosis)  # p-value


# Save results

# In[45]:


# kappa.to_excel("./outputs/tables/kappa.xlsx", float_format='%.3f')
# kappa.to_csv("./outputs/tables/kappa.csv", float_format='%.3f')


# %% Kappa score dataset generation (Supplementary Table 2(b))

# Compute kappa score

# In[46]:


kappa_list = []
names_list = []
raters = [('DNN', y_neuralnet), ('PTB_XL', y_true)]
for r1, r2 in combinations(raters, 2):
    name1, y1 = r1
    name2, y2 = r2
    negative_negative, positive_positive, positive_negative, negative_positive, _ = \
        affer_results(y1, y2)
    p_p = positive_positive.sum(axis=0)
    p_n = positive_negative.sum(axis=0)
    n_p = negative_positive.sum(axis=0)
    n_n = negative_negative.sum(axis=0)
    total_sum = p_p + p_n + n_p + n_n
    # Relative agreement
    r_agree = (p_p + n_n) / total_sum
    # Empirical probability of both saying yes
    p_yes = (p_p + p_n) * (p_p + n_p) / total_sum ** 2
    # Empirical probability of both saying no
    p_no = (n_n + n_p) * (n_n + p_n) / total_sum ** 2
    # Empirical probability of agreement
    p_agree = p_yes + p_no
    # Kappa score
    kappa = (r_agree - p_agree) / (1 - p_agree)
    kappa_list.append(kappa)
    names_list.append('{} vs {}'.format(name1, name2))


# In[47]:


kappas_annotators_and_DNN = pd.DataFrame(np.stack(kappa_list), columns=diagnosis, index=names_list)
print(kappas_annotators_and_DNN)
kappas_annotators_and_DNN.to_excel("./outputs/tables/kappas_annotators_and_DNN.xlsx", float_format='%.3f')
kappas_annotators_and_DNN.to_csv("./outputs/tables/kappas_annotators_and_DNN.csv", float_format='%.3f')


# %% Compute scores and bootstraped version of these scores on alternative splits

# In[48]:


# bootstrap_nsamples = 1000
# scores_resampled_list = []
# scores_percentiles_list = []
# for name in ['normal_order', 'date_order', 'individual_patients', 'base_model']:
#     print(name)
#     # Get data
#     yn_true = y_true
#     yn_score = np.load('./dnn_predicts/other_splits/model_'+name+'.npy') if not name == 'base_model' else y_score_best
#     # Compute threshold
#     nclasses = np.shape(yn_true)[1]
#     opt_precision, opt_recall, threshold = get_optimal_precision_recall(yn_true, yn_score)
#     mask_n = yn_score > threshold
#     yn_pred = np.zeros_like(yn_score)
#     yn_pred[mask_n] = 1
#     # Compute bootstraped samples
#     np.random.seed(123)  # NEVER change this =P
#     n, _ = np.shape(yn_true)
#     samples = np.random.randint(n, size=n * bootstrap_nsamples)
#     # Get samples
#     y_true_resampled = np.reshape(yn_true[samples, :], (bootstrap_nsamples, n, nclasses))
#     y_doctors_resampled = np.reshape(yn_pred[samples, :], (bootstrap_nsamples, n, nclasses))
#     # Apply functions
#     scores_resampled = np.array([get_scores(y_true_resampled[i, :, :], y_doctors_resampled[i, :, :], score_fun)
#                                  for i in range(bootstrap_nsamples)])
#     # Sort scores
#     scores_resampled.sort(axis=0)
#     # Append
#     scores_resampled_list.append(scores_resampled)

#     # Compute percentiles index
#     i = [int(p / 100.0 * bootstrap_nsamples) for p in percentiles]
#     # Get percentiles
#     scores_percentiles = scores_resampled[i, :, :]
#     # Convert percentiles to a dataframe
#     scores_percentiles_df = pd.concat([pd.DataFrame(x, index=diagnosis, columns=score_fun.keys())
#                                        for x in scores_percentiles], keys=['p1', 'p2'], axis=1)
#     # Change multiindex levels
#     scores_percentiles_df = scores_percentiles_df.swaplevel(0, 1, axis=1)
#     scores_percentiles_df = scores_percentiles_df.reindex(level=0, columns=score_fun.keys())
#     # Append
#     scores_percentiles_list.append(scores_percentiles_df)


# %% Print box plot on alternative splits (Supplementary Figure 2 (a))

# In[49]:


# scores_resampled_xr = xr.DataArray(np.array(scores_resampled_list),
#                                    dims=['predictor', 'n', 'diagnosis', 'score_fun'],
#                                    coords={
#                                     'predictor': ['random', 'by date', 'by patient', 'original DNN'],
#                                     'n': range(bootstrap_nsamples),
#                                     'diagnosis': ['1dAVb', 'RBBB', 'LBBB', 'SB', 'AF', 'ST'],
#                                     'score_fun': list(score_fun.keys())})
# # Remove everything except f1_score
# sf = 'F1 score'
# fig, ax = plt.subplots()
# f1_score_resampled_xr = scores_resampled_xr.sel(score_fun=sf)
# # Convert to dataframe
# f1_score_resampled_df = f1_score_resampled_xr.to_dataframe(name=sf).reset_index(level=[0, 1, 2])
# # Plot seaborn
# ax = sns.boxplot(x="diagnosis", y=sf, hue="predictor", data=f1_score_resampled_df,
#                  order=['1dAVb', 'SB', 'AF', 'ST', 'RBBB', 'LBBB'],
#                  palette=sns.color_palette("Set1", n_colors=8))
# plt.axvline(3.5, color='black', ls='--')
# plt.axvline(5.5, color='black', ls='--')
# plt.axvspan(3.5, 5.5, alpha=0.1, color='gray')
# # Save results
# plt.xticks(fontsize=16)
# plt.yticks(fontsize=16)
# plt.xlabel("")
# plt.ylabel("F1 score", fontsize=16)
# plt.legend(fontsize=17)
# plt.ylim([0.4, 1.05])
# plt.xlim([-0.5, 5.5])
# plt.tight_layout()
# plt.savefig('./outputs/figures/boxplot_bootstrap_other_splits_{0}.pdf'.format(sf))
# f1_score_resampled_df.to_csv('./outputs/figures/boxplot_bootstrap_other_splits_data.txt', index=False)

