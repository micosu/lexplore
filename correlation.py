import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Load and merge datasets
def load_and_merge_data(engineered_metrics, group_analysis):
    """Load both CSV files and merge them on student IDs"""
    
    print("Engineered Metrics Shape:", engineered_metrics.shape)
    print("Group Analysis Shape:", group_analysis.shape)
    
    # Merge datasets on student IDs
    merged_data = pd.merge(
        engineered_metrics, 
        group_analysis, 
        left_on='service_id', 
        right_on='id', 
        how='inner'
    )
    
    print("Merged Data Shape:", merged_data.shape)
    print("Missing values per column:")
    print(merged_data.isnull().sum())
    
    return merged_data

def preprocess_features(df):
    """Preprocess features: handle missing values, create bins, and standardize"""
    
    # Define the engineered metrics we want to analyze
    metric_columns = [
        'improved_learning_time', 'avg_response_time', 'learning_focus',
        'learning_efficiency', 'mission_persistence', 'accuracy',
        'gaming_behavior', 'speed_vs_accuracy', 'early_errors',
        'race_ratio', 'trained_exposures', 'trained_learned'
    ]
    
    # Create a copy for preprocessing
    processed_df = df.copy()
    
    # Handle missing values (fill with median for numerical columns)
    for col in metric_columns:
        if col in processed_df.columns:
            processed_df[col] = processed_df[col].fillna(processed_df[col].median())
    
    # Create categorical versions of some metrics that might benefit from binning
    binning_candidates = {
        'accuracy': {'bins': [0, 0.6, 0.8, 0.95, 1.0], 'labels': ['Low', 'Medium', 'High', 'Very High']},
        'mission_persistence': {'bins': [0, 0.3, 0.7, 1.0], 'labels': ['Low', 'Medium', 'High']},
        'learning_focus': {'bins': [0, 0.4, 0.7, 1.0], 'labels': ['Low', 'Medium', 'High']},
        'trained_exposures': {'bins': [0, 0.5, 0.8, 1.0], 'labels': ['Low', 'Medium', 'High']},
        'trained_learned': {'bins': [0, 0.3, 0.6, 1.0], 'labels': ['Low', 'Medium', 'High']}
    }
    
    # Create binned versions
    for metric, bin_info in binning_candidates.items():
        if metric in processed_df.columns:
            try:
                processed_df[f'{metric}_binned'] = pd.cut(
                    processed_df[metric], 
                    bins=bin_info['bins'], 
                    labels=bin_info['labels'], 
                    include_lowest=True
                )
            except Exception as e:
                print(f"Could not bin {metric}: {e}")
    
    # Standardize continuous features
    scaler = StandardScaler()
    continuous_features = [col for col in metric_columns if col in processed_df.columns]
    
    processed_df[continuous_features] = scaler.fit_transform(processed_df[continuous_features])
    
    print("Features standardized successfully")
    return processed_df, continuous_features, scaler

def create_target_variables(df):
    """Create binary target variables for improvement"""
    
    # Create binary targets for overall change
    df['overall_improved'] = (df['overall_change'] > 0).astype(int)
    df['overall_trained_improved'] = (df['overall_trained_change'] > 0).astype(int)
    
    # Also create more nuanced targets (significant improvement)
    overall_threshold = df['overall_change'].quantile(0.6)  # Top 40% improvers
    trained_threshold = df['overall_trained_change'].quantile(0.6)
    
    df['overall_high_improved'] = (df['overall_change'] >= overall_threshold).astype(int)
    df['trained_high_improved'] = (df['overall_trained_change'] >= trained_threshold).astype(int)
    
    print("Target variable distributions:")
    print(f"Overall Improved: {df['overall_improved'].value_counts()}")
    print(f"Trained Improved: {df['overall_trained_improved'].value_counts()}")
    print(f"High Overall Improved: {df['overall_high_improved'].value_counts()}")
    print(f"High Trained Improved: {df['trained_high_improved'].value_counts()}")
    
    return df

def correlation_analysis(df, continuous_features):
    """Perform correlation analysis between features and outcomes"""
    
    target_vars = ['overall_change', 'overall_trained_change', 'overall_improved', 'overall_trained_improved']
    
    # Calculate correlations
    correlation_results = {}
    
    for target in target_vars:
        if target in df.columns:
            correlations = df[continuous_features + [target]].corr()[target].drop(target)
            correlation_results[target] = correlations.sort_values(key=abs, ascending=False)
    
    # Display correlation results
    print("\n" + "="*60)
    print("CORRELATION ANALYSIS RESULTS")
    print("="*60)
    
    for target, corrs in correlation_results.items():
        print(f"\nTop correlations with {target}:")
        print("-" * 40)
        for feature, corr in corrs.head(8).items():
            significance = "***" if abs(corr) > 0.3 else "**" if abs(corr) > 0.2 else "*" if abs(corr) > 0.1 else ""
            print(f"{feature:25} {corr:8.4f} {significance}")
    
    # Create correlation heatmap
    plt.figure(figsize=(12, 10))
    correlation_matrix = df[continuous_features + target_vars].corr()
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
    sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='RdBu_r', center=0,
                square=True, fmt='.2f', cbar_kws={"shrink": .8})
    plt.title('Feature Correlation Matrix')
    plt.tight_layout()
    plt.show()
    
    return correlation_results

def train_and_evaluate_models(df, continuous_features):
    """Train and evaluate Logistic Regression, Random Forest, and AdaBoost models"""
    
    target_vars = ['overall_improved', 'overall_trained_improved', 'overall_high_improved', 'trained_high_improved']
    
    # Initialize models
    models = {
        'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10),
        'AdaBoost': AdaBoostClassifier(n_estimators=100, random_state=42)
    }
    
    results = {}
    feature_importance_results = {}
    
    for target in target_vars:
        if target not in df.columns:
            continue
            
        print(f"\n" + "="*60)
        print(f"ANALYSIS FOR TARGET: {target}")
        print("="*60)
        
        # Prepare features and target
        X = df[continuous_features].fillna(df[continuous_features].median())
        y = df[target]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        target_results = {}
        target_feature_importance = {}
        
        for model_name, model in models.items():
            # Train model
            model.fit(X_train, y_train)
            
            # Make predictions
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
            
            # Calculate metrics
            cv_scores = cross_val_score(model, X_train, y_train, cv=5)
            auc_score = roc_auc_score(y_test, y_pred_proba) if y_pred_proba is not None else None
            
            target_results[model_name] = {
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'test_accuracy': (y_pred == y_test).mean(),
                'auc_score': auc_score
            }
            
            # Feature importance
            if hasattr(model, 'coef_'):
                importance = abs(model.coef_[0])
            elif hasattr(model, 'feature_importances_'):
                importance = model.feature_importances_
            else:
                importance = None
            
            if importance is not None:
                feature_imp_df = pd.DataFrame({
                    'feature': continuous_features,
                    'importance': importance
                }).sort_values('importance', ascending=False)
                target_feature_importance[model_name] = feature_imp_df
            
            # Print results
            print(f"\n{model_name} Results:")
            print(f"  Cross-validation: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
            print(f"  Test accuracy: {target_results[model_name]['test_accuracy']:.4f}")
            if auc_score:
                print(f"  AUC Score: {auc_score:.4f}")
            
            # Print top features
            if model_name in target_feature_importance:
                print(f"  Top 5 Features:")
                for idx, row in feature_imp_df.head().iterrows():
                    print(f"    {row['feature']}: {row['importance']:.4f}")
        
        results[target] = target_results
        feature_importance_results[target] = target_feature_importance
    
    return results, feature_importance_results

def create_feature_importance_plot(feature_importance_results):
    """Create visualization of feature importance across models"""
    
    for target, model_results in feature_importance_results.items():
        if not model_results:
            continue
            
        plt.figure(figsize=(15, 8))
        
        subplot_idx = 1
        for model_name, feature_df in model_results.items():
            plt.subplot(1, len(model_results), subplot_idx)
            
            top_features = feature_df.head(10)
            plt.barh(range(len(top_features)), top_features['importance'])
            plt.yticks(range(len(top_features)), top_features['feature'], fontsize=8)
            plt.xlabel('Importance')
            plt.title(f'{model_name}\n({target})', fontsize=10)
            plt.gca().invert_yaxis()
            
            subplot_idx += 1
        
        plt.tight_layout()
        plt.suptitle(f'Feature Importance Comparison - {target}', y=1.02)
        plt.show()

def main_analysis(metrics, test_data):
    """Run the complete analysis pipeline"""
    
    print("Starting Student Performance Analysis")
    print("="*60)
    
    # Load and merge data
    merged_data = load_and_merge_data(metrics, test_data)
    
    # Preprocess features
    processed_data, continuous_features, scaler = preprocess_features(merged_data)
    
    # Create target variables
    processed_data = create_target_variables(processed_data)
    
    # Correlation analysis
    correlations = correlation_analysis(processed_data, continuous_features)
    
    # Model training and evaluation
    model_results, feature_importance = train_and_evaluate_models(processed_data, continuous_features)
    
    # Feature importance visualization
    create_feature_importance_plot(feature_importance)
    
    print("\n" + "="*60)
    print("SUMMARY OF KEY FINDINGS")
    print("="*60)
    
    # Summary of most important features across all analyses
    all_important_features = set()
    for target, models in feature_importance.items():
        for model, feature_df in models.items():
            all_important_features.update(feature_df.head(5)['feature'].tolist())
    
    print("Most frequently important features across all models:")
    for feature in sorted(all_important_features):
        print(f"  • {feature}")
    
    return processed_data, model_results, feature_importance, correlations

# Run the analysis
if __name__ == "__main__":
    # Load datasets
    engineered_metrics = pd.read_csv("during_study/new_results/june11/engineered_metrics.csv")
    group_analysis = pd.read_csv('group_analysis.csv')

    data, models, importance, corrs = main_analysis(engineered_metrics, group_analysis)