import tensorflow as tf

def optimize_model(model_path):
    converter = tf.lite.TFLiteConverter.from_saved_model(model_path)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()
    optimized_path = model_path + "_optimized.tflite"
    
    with open(optimized_path, "wb") as f:
        f.write(tflite_model)
    
    return optimized_path