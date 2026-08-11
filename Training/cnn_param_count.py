from tensorflow.keras.models import load_model

cnn_model = load_model('../Model/gesture_cnn_model.h5')
cnn_model.summary()