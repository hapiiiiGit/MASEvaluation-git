# Machine Learning Pipelines: Quick Start Guide

## Overview
This repository contains two machine learning pipelines:
1. **DNN Pipeline**: Classifies network traffic as malicious or safe using a Deep Neural Network (TensorFlow/Keras).
2. **CNN Pipeline**: Categorizes images of animals and vehicles using transfer learning with MobileNetV2 (TensorFlow/Keras).

---

## 1. DNN Pipeline: Network Traffic Classification

### Features
- Synthetic or real network traffic data (CSV format)
- Feature extraction and preprocessing
- Deep Neural Network (DNN) with TensorFlow/Keras
- Evaluation metrics: Accuracy, Precision, Recall, F1-score

### Quick Start
1. **Install dependencies:**
   ```bash
   pip install tensorflow scikit-learn pandas numpy
   ```
2. **Run the script:**
   ```bash
   python dnn_network_traffic.py
   ```
3. **Expected Output:**
   - Model training progress
   - Evaluation metrics printed to console

### Code Structure
- Data generation or loading
- Feature extraction and scaling
- Model definition and training
- Evaluation and metrics reporting

---

## 2. CNN Pipeline: Animal vs. Vehicle Image Classification

### Features
- Uses CIFAR-10 dataset (built-in to TensorFlow)
- Selects animal (cat, dog, horse) and vehicle (airplane, automobile, ship, truck) classes
- Images resized and preprocessed for MobileNetV2
- Transfer learning with MobileNetV2 (pre-trained on ImageNet)
- Evaluation metrics: Accuracy, Precision, Recall, F1-score

### Quick Start
1. **Install dependencies:**
   ```bash
   pip install tensorflow scikit-learn numpy
   ```
2. **Run the script:**
   ```bash
   python cnn_animals_vehicles.py
   ```
3. **Expected Output:**
   - Model training progress
   - Evaluation metrics printed to console

### Code Structure
- Data loading and class filtering
- Image resizing and preprocessing
- Transfer learning model setup
- Model training and evaluation

---

## Notes
- Both scripts are self-contained and can be run independently.
- For custom datasets, adjust the data loading and preprocessing sections accordingly.
- For further improvements, consider hyperparameter tuning, data augmentation, or using more advanced architectures.

---

## Contact
For questions or contributions, please contact the maintainer.
