/*
 Navicat Premium Data Transfer

 Source Server         : lllll
 Source Server Type    : MySQL
 Source Server Version : 90100 (9.1.0)
 Source Host           : localhost:3306
 Source Schema         : AttendanceSystem

 Target Server Type    : MySQL
 Target Server Version : 90100 (9.1.0)
 File Encoding         : 65001

 Date: 19/01/2025 22:04:02
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for AttendanceLogs
-- ----------------------------
DROP TABLE IF EXISTS `AttendanceLogs`;
CREATE TABLE `AttendanceLogs`  (
  `logId` bigint NOT NULL AUTO_INCREMENT,
  `sdtNhanVien` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `timeStart` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `statusStart` enum('SUCCESS','FAILED','NOT','NOT DEEPFAKE') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `isDeepfakeDetectedStart` tinyint(1) NOT NULL DEFAULT 0,
  `deepfakeScoreStart` float NOT NULL,
  `photoCapturedStart` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `timeEnd` timestamp NULL DEFAULT NULL,
  `statusEnd` enum('SUCCESS','FAILED','NOT','NOT DEEPFAKE') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'NOT',
  `isDeepfakeDetectedEnd` tinyint(1) NULL DEFAULT NULL,
  `deepfakeScoreEnd` float NULL DEFAULT NULL,
  `photoCapturedEnd` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  PRIMARY KEY (`logId`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 21 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of AttendanceLogs
-- ----------------------------
INSERT INTO `AttendanceLogs` VALUES (19, '033657673', '2025-01-18 21:12:10', 'FAILED', 0, 0, '/static/images/data/033657673_20250119041206065823.jpg', NULL, 'NOT', NULL, NULL, NULL);

-- ----------------------------
-- Table structure for DeepfakeLogs
-- ----------------------------
DROP TABLE IF EXISTS `DeepfakeLogs`;
CREATE TABLE `DeepfakeLogs`  (
  `deepfake_log_id` bigint NOT NULL AUTO_INCREMENT,
  `log_id` bigint NULL DEFAULT NULL,
  `detection_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `photo_analyzed` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  PRIMARY KEY (`deepfake_log_id`) USING BTREE,
  INDEX `log_id`(`log_id` ASC) USING BTREE,
  CONSTRAINT `DeepfakeLogs_ibfk_1` FOREIGN KEY (`log_id`) REFERENCES `AttendanceLogs` (`logId`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of DeepfakeLogs
-- ----------------------------

-- ----------------------------
-- Table structure for Departments
-- ----------------------------
DROP TABLE IF EXISTS `Departments`;
CREATE TABLE `Departments`  (
  `department_id` int NOT NULL AUTO_INCREMENT,
  `department_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`department_id`) USING BTREE,
  UNIQUE INDEX `department_name`(`department_name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of Departments
-- ----------------------------
INSERT INTO `Departments` VALUES (1, 'Phòng Kế Toán', '2025-01-16 18:51:20');
INSERT INTO `Departments` VALUES (2, 'Phòng IT', '2025-01-16 18:51:20');
INSERT INTO `Departments` VALUES (3, 'Phòng Nhân Sự', '2025-01-16 18:51:20');
INSERT INTO `Departments` VALUES (4, 'Phòng Sale', '2025-01-16 18:51:20');

-- ----------------------------
-- Table structure for Employees
-- ----------------------------
DROP TABLE IF EXISTS `Employees`;
CREATE TABLE `Employees`  (
  `maNhanVien` int NOT NULL AUTO_INCREMENT,
  `tenNhanVien` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `sdt` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `password` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `vaiTro` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `photo_reference` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `role` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `IsActive` bit(1) NULL DEFAULT b'1',
  `department_id` int NULL DEFAULT NULL,
  PRIMARY KEY (`maNhanVien`) USING BTREE,
  UNIQUE INDEX `email`(`email` ASC) USING BTREE,
  UNIQUE INDEX `sdt`(`sdt` ASC) USING BTREE,
  INDEX `department_id`(`department_id` ASC) USING BTREE,
  CONSTRAINT `Employees_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `Departments` (`department_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of Employees
-- ----------------------------
INSERT INTO `Employees` VALUES (1, 'admin', 'admin@gmail.com', '111111111', 'pass', 'admin', '/static/images/key-person.png', 'admin', '2025-01-18 06:08:20', b'1', 1);
INSERT INTO `Employees` VALUES (7, 'Trần Văn B', '1@gmail.com', '0333657671', 'pass', 'Dev', '/static/images/1_0333657671.jpg', 'user', '2025-01-18 06:16:23', b'1', 2);
INSERT INTO `Employees` VALUES (8, 'Trần Văn Chú', '2@gmail.com', '033656572', 'pass', 'dev', '/static/images/data/2_033656572.jpg', 'user', '2025-01-18 06:24:41', b'1', 1);
INSERT INTO `Employees` VALUES (9, 'thành', 'a3@gmail.com', '033657673', 'pass', 'dev', '/static/images/data/a3_033657673.jpg', 'user', '2025-01-18 06:30:20', b'1', 1);

SET FOREIGN_KEY_CHECKS = 1;
