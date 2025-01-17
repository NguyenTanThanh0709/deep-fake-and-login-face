class AttendanceLog:
    def __init__(self, logId, maNhanVien, timeStart, statusStart, isDeepfakeDetectedStart, deepfakeScoreStart, photoCapturedStart,
                 timeEnd, statusEnd, isDeepfakeDetectedEnd, deepfakeScoreEnd, photoCapturedEnd):
        self.logId = logId
        self.maNhanVien = maNhanVien
        self.timeStart = timeStart
        self.statusStart = statusStart
        self.isDeepfakeDetectedStart = isDeepfakeDetectedStart
        self.deepfakeScoreStart = deepfakeScoreStart
        self.photoCapturedStart = photoCapturedStart
        self.timeEnd = timeEnd
        self.statusEnd = statusEnd
        self.isDeepfakeDetectedEnd = isDeepfakeDetectedEnd
        self.deepfakeScoreEnd = deepfakeScoreEnd
        self.photoCapturedEnd = photoCapturedEnd

    @staticmethod
    def from_dict(data):
        return AttendanceLog(
            logId=data.get('logId'),
            maNhanVien=data.get('maNhanVien'),
            timeStart=data.get('timeStart'),
            statusStart=data.get('statusStart'),
            isDeepfakeDetectedStart=data.get('isDeepfakeDetectedStart'),
            deepfakeScoreStart=data.get('deepfakeScoreStart'),
            photoCapturedStart=data.get('photoCapturedStart'),
            timeEnd=data.get('timeEnd'),
            statusEnd=data.get('statusEnd'),
            isDeepfakeDetectedEnd=data.get('isDeepfakeDetectedEnd'),
            deepfakeScoreEnd=data.get('deepfakeScoreEnd'),
            photoCapturedEnd=data.get('photoCapturedEnd')
        )

    def to_dict(self):
        return {
            "logId": self.logId,
            "maNhanVien": self.maNhanVien,
            "timeStart": self.timeStart,
            "statusStart": self.statusStart,
            "isDeepfakeDetectedStart": self.isDeepfakeDetectedStart,
            "deepfakeScoreStart": self.deepfakeScoreStart,
            "photoCapturedStart": self.photoCapturedStart,
            "timeEnd": self.timeEnd,
            "statusEnd": self.statusEnd,
            "isDeepfakeDetectedEnd": self.isDeepfakeDetectedEnd,
            "deepfakeScoreEnd": self.deepfakeScoreEnd,
            "photoCapturedEnd": self.photoCapturedEnd
        }
