"""
Evaluation Module

This module implements evaluation metrics for the screening system:
- Precision
- Recall
- F1 Score

These metrics evaluate how well the system ranks candidates
against known good/bad matches.
"""

import logging
from typing import List, Tuple
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


ERROR_MSG_LENGTH = "Labels and predictions must have same length"

def precision(true_labels: List[int], predicted_labels: List[int]) -> float:
    """
    Calculate precision score.
    
    Precision = TP / (TP + FP)
    = Portion of positive predictions that were correct
    
    Args:
        true_labels (List[int]): True labels (1 for relevant, 0 for not relevant)
        predicted_labels (List[int]): Predicted labels
        
    Returns:
        float: Precision score (0-1)
    """
    try:
        if len(true_labels) != len(predicted_labels):
            raise ValueError(ERROR_MSG_LENGTH)
        
        true_positives = sum(1 for true, pred in zip(true_labels, predicted_labels)
                           if true == 1 and pred == 1)
        
        false_positives = sum(1 for true, pred in zip(true_labels, predicted_labels)
                            if true == 0 and pred == 1)
        
        denominator = true_positives + false_positives
        
        if denominator == 0:
            logger.warning("No positive predictions found")
            return 0.0
        
        precision_score = true_positives / denominator
        logger.info(f"Precision: {precision_score:.4f}")
        return round(precision_score, 4)
        
    except Exception as e:
        logger.error(f"Error calculating precision: {e}")
        return 0.0


def recall(true_labels: List[int], predicted_labels: List[int]) -> float:
    """
    Calculate recall score.
    
    Recall = TP / (TP + FN)
    = Portion of actual positive cases correctly identified
    
    Args:
        true_labels (List[int]): True labels (1 for relevant, 0 for not relevant)
        predicted_labels (List[int]): Predicted labels
        
    Returns:
        float: Recall score (0-1)
    """
    try:
        if len(true_labels) != len(predicted_labels):
            raise ValueError(ERROR_MSG_LENGTH)
        
        true_positives = sum(1 for true, pred in zip(true_labels, predicted_labels)
                           if true == 1 and pred == 1)
        
        false_negatives = sum(1 for true, pred in zip(true_labels, predicted_labels)
                            if true == 1 and pred == 0)
        
        denominator = true_positives + false_negatives
        
        if denominator == 0:
            logger.warning("No positive labels found")
            return 0.0
        
        recall_score = true_positives / denominator
        logger.info(f"Recall: {recall_score:.4f}")
        return round(recall_score, 4)
        
    except Exception as e:
        logger.error(f"Error calculating recall: {e}")
        return 0.0


def f1_score(true_labels: List[int], predicted_labels: List[int]) -> float:
    """
    Calculate F1 score (harmonic mean of precision and recall).
    
    F1 = 2 * (Precision * Recall) / (Precision + Recall)
    
    Args:
        true_labels (List[int]): True labels (1 for relevant, 0 for not relevant)
        predicted_labels (List[int]): Predicted labels
        
    Returns:
        float: F1 score (0-1)
    """
    try:
        prec = precision(true_labels, predicted_labels)
        rec = recall(true_labels, predicted_labels)
        
        denominator = prec + rec
        
        if denominator == 0:
            logger.warning("Both precision and recall are 0")
            return 0.0
        
        f1 = 2 * (prec * rec) / denominator
        logger.info(f"F1 Score: {f1:.4f}")
        return round(f1, 4)
        
    except Exception as e:
        logger.error(f"Error calculating F1 score: {e}")
        return 0.0


def evaluate_model(true_labels: List[int], 
                   predicted_labels: List[int]) -> dict:
    """
    Comprehensive model evaluation.
    
    Args:
        true_labels (List[int]): True labels (1 for relevant, 0 for not relevant)
        predicted_labels (List[int]): Predicted labels
        
    Returns:
        dict: Dictionary containing precision, recall, and F1 score
    """
    try:
        if len(true_labels) != len(predicted_labels):
            raise ValueError(ERROR_MSG_LENGTH)
        
        if len(true_labels) == 0:
            raise ValueError("Empty labels provided")
        
        prec = precision(true_labels, predicted_labels)
        rec = recall(true_labels, predicted_labels)
        f1 = f1_score(true_labels, predicted_labels)
        
        # Calculate additional metrics
        accuracy = sum(1 for true, pred in zip(true_labels, predicted_labels)
                      if true == pred) / len(true_labels)
        
        metrics = {
            'precision': prec,
            'recall': rec,
            'f1_score': f1,
            'accuracy': round(accuracy, 4)
        }
        
        logger.info(f"Model Evaluation Complete: {metrics}")
        return metrics
        
    except Exception as e:
        logger.error(f"Error during model evaluation: {e}")
        raise


def accuracy_score(true_labels: List[int], predicted_labels: List[int]) -> float:
    """
    Calculate accuracy score.
    
    Accuracy = (TP + TN) / (TP + TN + FP + FN)
    
    Args:
        true_labels (List[int]): True labels
        predicted_labels (List[int]): Predicted labels
        
    Returns:
        float: Accuracy score (0-1)
    """
    try:
        if len(true_labels) != len(predicted_labels):
            raise ValueError(ERROR_MSG_LENGTH)
        
        correct = sum(1 for true, pred in zip(true_labels, predicted_labels)
                     if true == pred)
        
        accuracy = correct / len(true_labels)
        logger.info(f"Accuracy: {accuracy:.4f}")
        return round(accuracy, 4)
        
    except Exception as e:
        logger.error(f"Error calculating accuracy: {e}")
        return 0.0


def get_confusion_matrix(true_labels: List[int], 
                        predicted_labels: List[int]) -> dict:
    """
    Calculate confusion matrix components.
    
    Args:
        true_labels (List[int]): True labels
        predicted_labels (List[int]): Predicted labels
        
    Returns:
        dict: Confusion matrix with TP, TN, FP, FN
    """
    try:
        tp = sum(1 for true, pred in zip(true_labels, predicted_labels)
                if true == 1 and pred == 1)
        tn = sum(1 for true, pred in zip(true_labels, predicted_labels)
                if true == 0 and pred == 0)
        fp = sum(1 for true, pred in zip(true_labels, predicted_labels)
                if true == 0 and pred == 1)
        fn = sum(1 for true, pred in zip(true_labels, predicted_labels)
                if true == 1 and pred == 0)
        
        return {
            'true_positives': tp,
            'true_negatives': tn,
            'false_positives': fp,
            'false_negatives': fn
        }
        
    except Exception as e:
        logger.error(f"Error calculating confusion matrix: {e}")
        return {'true_positives': 0, 'true_negatives': 0, 
                'false_positives': 0, 'false_negatives': 0}


# ============================================================================
# Ranking-based Evaluation Metrics (Precision@K, Recall@K, Mean Average Precision)
# ============================================================================

def precision_at_k(df, k: int, relevant_column: str = 'category', 
                  relevant_value: str = None) -> float:
    """
    Calculate Precision@K for a single relevant category.
    
    Precision@K = (number of relevant items in top-k) / k
    
    Args:
        df: DataFrame with ranking results sorted by relevance score
        k (int): Number of top items to consider
        relevant_column (str): Column name containing category/label
        relevant_value (str): The value that indicates relevance
        
    Returns:
        float: Precision@K score (0-1)
    """
    try:
        if k <= 0 or len(df) == 0:
            logger.warning("Invalid k value or empty dataframe")
            return 0.0
        
        if relevant_value is None:
            raise ValueError("relevant_value must be specified")
        
        top_k = df.head(k)
        relevant_count = len(top_k[top_k[relevant_column] == relevant_value])
        
        precision_score = relevant_count / k
        return round(precision_score, 4)
        
    except Exception as e:
        logger.error(f"Error calculating Precision@{k}: {e}")
        return 0.0


def recall_at_k(df, k: int, relevant_column: str = 'category',
               relevant_value: str = None) -> float:
    """
    Calculate Recall@K for a single relevant category.
    
    Recall@K = (number of relevant items in top-k) / (total relevant items)
    
    Args:
        df: DataFrame with ranking results sorted by relevance score
        k (int): Number of top items to consider
        relevant_column (str): Column name containing category/label
        relevant_value (str): The value that indicates relevance
        
    Returns:
        float: Recall@K score (0-1)
    """
    try:
        if k <= 0 or len(df) == 0:
            logger.warning("Invalid k value or empty dataframe")
            return 0.0
        
        if relevant_value is None:
            raise ValueError("relevant_value must be specified")
        
        total_relevant = len(df[df[relevant_column] == relevant_value])
        
        if total_relevant == 0:
            logger.warning(f"No relevant items found for value: {relevant_value}")
            return 0.0
        
        top_k = df.head(k)
        relevant_in_top_k = len(top_k[top_k[relevant_column] == relevant_value])
        
        recall_score = relevant_in_top_k / total_relevant
        return round(recall_score, 4)
        
    except Exception as e:
        logger.error(f"Error calculating Recall@{k}: {e}")
        return 0.0


def precision_at_k_multi(df, k: int, relevant_column: str = 'category',
                        relevant_values: List[str] = None) -> float:
    """
    Calculate Precision@K for multiple relevant categories.
    
    Args:
        df: DataFrame with ranking results sorted by relevance score
        k (int): Number of top items to consider
        relevant_column (str): Column name containing category/label
        relevant_values (List[str]): List of values that indicate relevance
        
    Returns:
        float: Precision@K score (0-1)
    """
    try:
        if k <= 0 or len(df) == 0 or not relevant_values:
            logger.warning("Invalid parameters")
            return 0.0
        
        top_k = df.head(k)
        relevant_count = len(top_k[top_k[relevant_column].isin(relevant_values)])
        
        precision_score = relevant_count / k
        return round(precision_score, 4)
        
    except Exception as e:
        logger.error(f"Error calculating Precision@{k} (multi): {e}")
        return 0.0


def recall_at_k_multi(df, k: int, relevant_column: str = 'category',
                     relevant_values: List[str] = None) -> float:
    """
    Calculate Recall@K for multiple relevant categories.
    
    Args:
        df: DataFrame with ranking results sorted by relevance score
        k (int): Number of top items to consider
        relevant_column (str): Column name containing category/label
        relevant_values (List[str]): List of values that indicate relevance
        
    Returns:
        float: Recall@K score (0-1)
    """
    try:
        if k <= 0 or len(df) == 0 or not relevant_values:
            logger.warning("Invalid parameters")
            return 0.0
        
        total_relevant = len(df[df[relevant_column].isin(relevant_values)])
        
        if total_relevant == 0:
            logger.warning(f"No relevant items found")
            return 0.0
        
        top_k = df.head(k)
        relevant_in_top_k = len(top_k[top_k[relevant_column].isin(relevant_values)])
        
        recall_score = relevant_in_top_k / total_relevant
        return round(recall_score, 4)
        
    except Exception as e:
        logger.error(f"Error calculating Recall@{k} (multi): {e}")
        return 0.0


def mean_average_precision(df, relevant_column: str = 'category',
                          relevant_value: str = None) -> float:
    """
    Calculate Mean Average Precision (MAP) for a single category.
    
    MAP considers the ranking position of relevant items and averages precision
    scores across all relevant positions.
    
    Args:
        df: DataFrame with ranking results sorted by relevance score
        relevant_column (str): Column name containing category/label
        relevant_value (str): The value that indicates relevance
        
    Returns:
        float: MAP score (0-1)
    """
    try:
        if len(df) == 0 or relevant_value is None:
            logger.warning("Invalid parameters")
            return 0.0
        
        relevant_count = 0
        precisions = []
        
        for i, row in enumerate(df.itertuples()):
            if getattr(row, relevant_column) == relevant_value:
                relevant_count += 1
                precisions.append(relevant_count / (i + 1))
        
        if len(precisions) == 0:
            logger.warning(f"No relevant items found for value: {relevant_value}")
            return 0.0
        
        map_score = sum(precisions) / len(precisions)
        return round(map_score, 4)
        
    except Exception as e:
        logger.error(f"Error calculating MAP: {e}")
        return 0.0


def mean_average_precision_multi(df, relevant_column: str = 'category',
                                relevant_values: List[str] = None) -> float:
    """
    Calculate Mean Average Precision (MAP) for multiple categories.
    
    Args:
        df: DataFrame with ranking results sorted by relevance score
        relevant_column (str): Column name containing category/label
        relevant_values (List[str]): List of values that indicate relevance
        
    Returns:
        float: MAP score (0-1)
    """
    try:
        if len(df) == 0 or not relevant_values:
            logger.warning("Invalid parameters")
            return 0.0
        
        relevant_count = 0
        precisions = []
        
        for i, row in enumerate(df.itertuples()):
            if getattr(row, relevant_column) in relevant_values:
                relevant_count += 1
                precisions.append(relevant_count / (i + 1))
        
        if len(precisions) == 0:
            logger.warning(f"No relevant items found")
            return 0.0
        
        map_score = sum(precisions) / len(precisions)
        return round(map_score, 4)
        
    except Exception as e:
        logger.error(f"Error calculating MAP (multi): {e}")
        return 0.0


def evaluate_ranking_models(results_dict: dict, k: int = 10,
                           relevant_column: str = 'category',
                           relevant_values: List[str] = None) -> dict:
    """
    Comprehensive evaluation of multiple ranking models.
    
    Args:
        results_dict (dict): Dictionary with model names as keys and
                            ranked DataFrames as values
        k (int): K value for Precision@K and Recall@K metrics
        relevant_column (str): Column name containing category/label
        relevant_values (List[str]): List of values that indicate relevance
        
    Returns:
        dict: Dictionary with evaluation results for each model
    """
    try:
        if not results_dict or not relevant_values:
            raise ValueError("Invalid input parameters")
        
        evaluation_results = {}
        
        for model_name, df in results_dict.items():
            metrics = {
                'Precision@10': precision_at_k_multi(df, k, relevant_column, relevant_values),
                'Recall@10': recall_at_k_multi(df, k, relevant_column, relevant_values),
                'MAP': mean_average_precision_multi(df, relevant_column, relevant_values)
            }
            evaluation_results[model_name] = metrics
        
        logger.info(f"Model evaluation complete: {evaluation_results}")
        return evaluation_results
        
    except Exception as e:
        logger.error(f"Error in model evaluation: {e}")
        return {}
