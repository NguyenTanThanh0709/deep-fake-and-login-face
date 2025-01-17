class DeepfakeLog:
    def __init__(self, deepfake_log_id, log_id, detection_time, deepfake_score, prediction, photo_analyzed):
        self.deepfake_log_id = deepfake_log_id
        self.log_id = log_id
        self.detection_time = detection_time
        self.deepfake_score = deepfake_score
        self.prediction = prediction
        self.photo_analyzed = photo_analyzed

    @staticmethod
    def from_dict(data):
        return DeepfakeLog(
            deepfake_log_id=data.get('deepfake_log_id'),
            log_id=data.get('log_id'),
            detection_time=data.get('detection_time'),
            deepfake_score=data.get('deepfake_score'),
            prediction=data.get('Prediction'),
            photo_analyzed=data.get('photo_analyzed')
        )

    def to_dict(self):
        return {
            "deepfake_log_id": self.deepfake_log_id,
            "log_id": self.log_id,
            "detection_time": self.detection_time,
            "deepfake_score": self.deepfake_score,
            "prediction": self.prediction,
            "photo_analyzed": self.photo_analyzed
        }
