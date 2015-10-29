from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_samples, silhouette_score

from matplotlib import pyplot as plt
import matplotlib.cm as cm
import numpy as np


def silhouette_analysis(X, range_n_clusters = range(2,103, 20), 
                        func=AgglomerativeClustering, 
                        params_dict=None,
                        plot=True):
    """performs silhouette analysis on dataset X for range_n_clusters"""
    
    #set default params if performing Agglomerative Clustering
    if params_dict == None and func==AgglomerativeClustering:
        # params_dict = {'linkage':'average'}
        params_dict = {'linkage':'ward'}

    silhouette_avgs = []
    for n_clusters in range_n_clusters:
        
        clusterer = func(n_clusters=n_clusters, **params_dict)
        cluster_labels = clusterer.fit_predict(X)
        silhouette_avg = silhouette_score(X, cluster_labels)
        print("For n_clusters =", n_clusters,
              "The average silhouette_score is :", silhouette_avg)
        silhouette_avgs.append(silhouette_avg)

        if plot:
            fig, ax1 = plt.subplots(1, 1)

            # The 1st subplot is the silhouette plot
            # The silhouette coefficient can range from -1, 1 if it's very low, then 
            # the clustering sucks and that's that.
            ax1.set_xlim([-0.1, 1])

            #the  (n_clusters + 1) * 10 makes space in the graph
            ax1.set_ylim([0, len(X) + (n_clusters + 1) * 10])

            # Compute the silhouette scores for each sample
            sample_silhouette_values = silhouette_samples(X, cluster_labels)

            y_lower = 10
            for i in range(n_clusters):
                # Aggregate the silhouette scores for samples belonging to
                # cluster i, and sort them
                ith_cluster_silhouette_values = \
                    sample_silhouette_values[cluster_labels == i]

                ith_cluster_silhouette_values.sort()

                size_cluster_i = ith_cluster_silhouette_values.shape[0]
                y_upper = y_lower + size_cluster_i

                color = cm.spectral(float(i) / n_clusters)
                ax1.fill_betweenx(np.arange(y_lower, y_upper),
                                  0, ith_cluster_silhouette_values,
                                  facecolor=color, edgecolor=color, alpha=0.7)

                # Label the silhouette plots with their cluster numbers at the middle
                ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

                # Compute the new y_lower for next plot
                y_lower = y_upper + 10  # 10 for the 0 samples

            ax1.set_title("The silhouette plot for the various clusters.")
            ax1.set_xlabel("The silhouette coefficient values")
            ax1.set_ylabel("Cluster label")

            # The vertical line for average silhoutte score of all the values
            ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

            ax1.set_yticks([])  # Clear the yaxis labels / ticks
            ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

            

            plt.suptitle(("Silhouette analysis for hierarchical clustering on sample data "
                          "with n_clusters = %d" % n_clusters),
                         fontsize=14, fontweight='bold')

    plt.figure()
    plt.plot(range_n_clusters, silhouette_avgs)
    plt.title('Silhouette Scores for n clusters')
    ax = plt.gca()
    ax.set_xlabel('n clusters')
    ax.set_ylabel('Silhouette Scores')

