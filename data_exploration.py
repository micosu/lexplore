from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import sys
from statsmodels.formula.api import ols


def explore_binning(data, metric, metric_name=None, bin_range=(3, 9)):
    if not metric_name:
        metric_name = metric
    # Sturges' rule - good starting point
    n_bins_sturges = int(np.ceil(np.log2(len(data[metric])) + 1))

    # Freedman-Diaconis rule - robust to outliers
    q75, q25 = np.percentile(data[metric], [75, 25])
    iqr = q75 - q25
    bin_width = 2 * iqr / (len(data[metric]) ** (1/3))
    n_bins_fd = int(np.ceil((data[metric].max() - data[metric].min()) / bin_width))

    print(f"Sturges suggests {n_bins_sturges} bins")
    print(f"Freedman-Diaconis suggests {n_bins_fd} bins")

    # fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    # axes = axes.flatten()

    fig, ax = plt.subplots(1, 1, figsize=(8, 6))  # Just one subplot

    counts, bins, patches = ax.hist(data[metric], bins='auto', alpha=0.7, edgecolor='black')
    ax.set_title(f'{metric_name} - Auto bins')
    ax.set_xlabel(metric_name)
    ax.set_ylabel('Count')

    # Add count labels on bars
    for j, (count, bin_edge) in enumerate(zip(counts, bins[:-1])):
        if count >= 12:
            ax.text(bin_edge + (bins[1]-bins[0])/2, count + 0.5, 
                f'{int(count)}', ha='center', va='bottom', 
                color='green', fontweight='bold')
        else:
            ax.text(bin_edge + (bins[1]-bins[0])/2, count + 0.5, 
                f'{int(count)}', ha='center', va='bottom', 
                color='red')
    
    # for i, n_bins in enumerate(range(bin_range[0], bin_range[1]+1)):
    #     if i < len(axes):
    #         counts, bins, patches = axes[i].hist(data[metric], bins='auto', alpha=0.7, edgecolor='black')
    #         axes[i].set_title(f'{metric_name} - {n_bins} bins')
    #         axes[i].set_xlabel(metric_name)
    #         axes[i].set_ylabel('Count')
            
    #         # Add count labels on bars
    #         for j, (count, bin_edge) in enumerate(zip(counts, bins[:-1])):
    #             if count >= 12:  # Highlight bins with enough students
    #                 axes[i].text(bin_edge + (bins[1]-bins[0])/2, count + 0.5, 
    #                            f'{int(count)}', ha='center', va='bottom', 
    #                            color='green', fontweight='bold')
    #             else:
    #                 axes[i].text(bin_edge + (bins[1]-bins[0])/2, count + 0.5, 
    #                            f'{int(count)}', ha='center', va='bottom', 
    #                            color='red')
    
    plt.tight_layout()
    plt.show()
    return bins


def find_optimal_clusters(data, metric, max_clusters=8):
    data_reshaped = data[metric].values.reshape(-1, 1)
    
    silhouette_scores = []
    inertias = []

    best_k,best_score = 0,0
    
    for k in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=k, random_state=42)
        cluster_labels = kmeans.fit_predict(data_reshaped)
        
        # Check if all clusters have at least 12 students
        unique, counts = np.unique(cluster_labels, return_counts=True)
        min_cluster_size = counts.min()
        
        if min_cluster_size >= 15:
            silhouette_avg = silhouette_score(data_reshaped, cluster_labels)
            silhouette_scores.append((k, silhouette_avg))
            inertias.append((k, kmeans.inertia_))
            print(f"K={k}: Silhouette Score={silhouette_avg:.3f}, Min cluster size={min_cluster_size}")
            if silhouette_avg > best_score:
                best_score, best_k = silhouette_avg, k
        else:
            print(f"K={k}: Rejected - min cluster size={min_cluster_size} < 12")
    
    return silhouette_scores, inertias, best_k

# Fit K-means with 3 clusters
def fit_kmeans(data, metric, n_clusters):
    data_reshaped = data[metric].values.reshape(-1, 1) # type: ignore[attr-defined]
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(data_reshaped)

    # Add cluster labels to your dataframe
    data['cluster'] = cluster_labels

    # Visualize the clusters
    plt.figure(figsize=(12, 5))

    # Plot 1: Histogram with cluster colors
    plt.subplot(1, 2, 1)
    colors = ['red', 'blue', 'green']
    for i in range(n_clusters):
        cluster_data = data[data['cluster'] == i][metric]
        plt.hist(cluster_data, bins=10, alpha=0.7, label=f'Cluster {i} (n={len(cluster_data)})', 
                color=colors[i], edgecolor='black')

    plt.xlabel(metric)
    plt.ylabel('Number of Students')
    plt.title(f'{metric} - {n_clusters} Natural Clusters')
    plt.legend()

    # Plot 2: Scatter plot to see cluster boundaries
    plt.subplot(1, 2, 2)
    for i in range(n_clusters):
        cluster_data = data[data['cluster'] == i][metric]
        plt.scatter(cluster_data, [i] * len(cluster_data), 
                    c=colors[i], alpha=0.6, s=50, label=f'Cluster {i}')

    plt.xlabel(metric)
    plt.ylabel('Cluster')
    plt.title('Cluster Assignments')
    plt.legend()
    plt.tight_layout()
    plt.show()

    # Print cluster statistics
    print("Cluster Statistics:")
    for i in range(n_clusters):
        cluster_data = data[data['cluster'] == i][metric]
        print(f"Cluster {i}: n={len(cluster_data)}, mean={cluster_data.mean():.1f}, "
            f"range=({cluster_data.min()}-{cluster_data.max()})")

def test_group_normality(data, metric, bins):
        # Create your bins
        bins = pd.cut(data[metric], bins=bins, include_lowest=True)

        # Extract the actual groups (lists of student values)
        groups = []
        for bin_category in bins.cat.categories:
            group_data = data[metric][bins == bin_category]
            if len(group_data) > 0:
                groups.append(group_data.values)

        # Check each group
        for i, group in enumerate(groups):
            print(f"Group {i}: n={len(group)}, mean={group.mean():.1f}")
            
            if len(group) >= 8:
                from scipy.stats import shapiro
                _, p_val = shapiro(group)
                normal = "Normal" if p_val > 0.05 else "Not normal"
                print(f"  {normal} (p={p_val:.3f})")
                
                if p_val > 0.05 or len(group) >= 15:
                    print(f"  ✓ OK to use")
                else:
                    print(f"  ✗ Too small AND not normal")
            else:
                print(f"  ✗ Too small for testing")
       

if __name__ == "__main__":
    student_metrics = pd.read_csv(f"student_metrics.csv")
    # student_scores = pd.read_csv("fourth_test_metrics.csv")
    # student_metrics = student_metrics.merge(student_scores, left_on="service_id", right_on="id", how="inner")
    metric = "words_with_4plus_exposures"
    print("RESULTS FOR METRIC: ", metric)
    # Look for visual separations
    bin_edges = explore_binning(student_metrics, metric)
    print("Bin edges: ", [float(i) for i in bin_edges])
    # bin_edges = [4.49, 56.11894737, 107.74789474, 159.37684211, 211.00578947, 985.44] # total playtime
    # bin_edges = [2.0, 34.166, 66.333, 98.5, 130.666, 388.0] # total_pns
    # bin_edges = [1.0, 3.623333333333333, 4.27917, 4.935, 5.590833333333332, 6.246666666666666, 8.87] # average interactions
    # bin_edges = [1.0,4.577272727272726, 5.292727272727272, 6.008181818181818, 8.87] # average interactions fourth only
    bin_edges = [0.0, 5.666666666666667, 11.333333333333334, 17.0, 22.666666666666668, 28.333333333333336, 68.0] # learned words
    print("Checking whether each of our groups are ok to use with ANOVA")
    test_group_normality(student_metrics, metric, bin_edges)
    # Use kmeans
    sil_scores, inertias, k = find_optimal_clusters(student_metrics, metric)
    print("k is ", k)
    if k <= 0:
        print("No ideal clustering for this metric")
    else:
        fit_kmeans(student_metrics, metric, k)

    # ANOVA analyses
    student_scores = pd.read_csv("test_metrics.csv")
    all_metrics = student_metrics.merge(student_scores, left_on="service_id", right_on="id", how="inner")
    # all_metrics = student_metrics
    print(f"Size of student metrics: {len(student_metrics)}; Size of Student Scores: {len(student_scores)}; Size of combined: {len(all_metrics)}")

    all_metrics['bin_group'] = pd.cut(all_metrics[metric], bins=bin_edges, include_lowest=True)
    # ANOVA based on binning
    print("ANOVA Results - Binning:")
    model = ols('overall_change ~ C(bin_group)', data=all_metrics).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    print(anova_table)

    if k <= 0:
        sys.exit() 
    # ANOVA based on k-means clusters
    print("\nANOVA Results - K-means:")
    model = ols('overall_change ~ C(cluster)', data=all_metrics).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)
    print(anova_table)


    # Optional: print metrics with labels applied
    # all_metrics.to_csv(f"all_metrics.csv", index=False)
