class AttendanceLog:
    def __init__(self, logId, sdtNhanVien, timeStart, statusStart, isDeepfakeDetectedStart, deepfakeScoreStart, photoCapturedStart,
                 timeEnd, statusEnd, isDeepfakeDetectedEnd, deepfakeScoreEnd, photoCapturedEnd, LinkVideoDeepFakeStart, LinkVideoDeepFakeEnd,
                 StatusDeepFakeStart, StatusDeepFakeEnd,latStart,lonStart,latEnd,lonEnd):
        self.logId = logId
        self.sdtNhanVien = sdtNhanVien
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
        self.LinkVideoDeepFakeStart = LinkVideoDeepFakeStart
        self.LinkVideoDeepFakeEnd = LinkVideoDeepFakeEnd
        self.StatusDeepFakeStart = StatusDeepFakeStart
        self.StatusDeepFakeEnd = StatusDeepFakeEnd
        self.latStart = latStart
        self.lonStart = lonStart
        self.latEnd = latEnd
        self.lonEnd = lonEnd
        

    @staticmethod
    def from_dict(data):
        return AttendanceLog(
            logId=data.get('logId'),
            sdtNhanVien=data.get('sdtNhanVien'),
            timeStart=data.get('timeStart'),
            statusStart=data.get('statusStart'),
            isDeepfakeDetectedStart=data.get('isDeepfakeDetectedStart'),
            deepfakeScoreStart=data.get('deepfakeScoreStart'),
            photoCapturedStart=data.get('photoCapturedStart'),
            timeEnd=data.get('timeEnd'),
            statusEnd=data.get('statusEnd'),
            isDeepfakeDetectedEnd=data.get('isDeepfakeDetectedEnd'),
            deepfakeScoreEnd=data.get('deepfakeScoreEnd'),
            photoCapturedEnd=data.get('photoCapturedEnd'),
            LinkVideoDeepFakeStart=data.get('LinkVideoDeepFakeStart'),
            LinkVideoDeepFakeEnd=data.get('LinkVideoDeepFakeEnd'),
            StatusDeepFakeStart=data.get('StatusDeepFakeStart'),
            StatusDeepFakeEnd=data.get('StatusDeepFakeEnd'),
            latStart=data.get('latStart'),
            lonStart=data.get('lonStart'),
            latEnd=data.get('latEnd'),
            lonEnd=data.get('lonEnd')
        )

    def to_dict(self):
        return {
            "logId": self.logId,
            "sdtNhanVien": self.sdtNhanVien,
            "timeStart": self.timeStart,
            "statusStart": self.statusStart,
            "isDeepfakeDetectedStart": self.isDeepfakeDetectedStart,
            "deepfakeScoreStart": self.deepfakeScoreStart,
            "photoCapturedStart": self.photoCapturedStart,
            "timeEnd": self.timeEnd,
            "statusEnd": self.statusEnd,
            "isDeepfakeDetectedEnd": self.isDeepfakeDetectedEnd,
            "deepfakeScoreEnd": self.deepfakeScoreEnd,
            "photoCapturedEnd": self.photoCapturedEnd,
            "LinkVideoDeepFakeStart": self.LinkVideoDeepFakeStart,
            "LinkVideoDeepFakeEnd": self.LinkVideoDeepFakeEnd,
            "StatusDeepFakeStart": self.StatusDeepFakeStart,
            "StatusDeepFakeEnd": self.StatusDeepFakeEnd,
            "latStart": self.latStart,
            "lonStart": self.lonStart,
            "latEnd": self.latEnd,
            "lonEnd": self.lonEnd
        }
