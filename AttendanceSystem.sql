/*
 Navicat Premium Data Transfer

 Source Server         : root
 Source Server Type    : MySQL
 Source Server Version : 90200 (9.2.0)
 Source Host           : localhost:3306
 Source Schema         : attendancesystem

 Target Server Type    : MySQL
 Target Server Version : 90200 (9.2.0)
 File Encoding         : 65001

 Date: 08/02/2025 01:28:40
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for attendancelogs
-- ----------------------------
DROP TABLE IF EXISTS `attendancelogs`;
CREATE TABLE `attendancelogs`  (
  `logId` bigint NOT NULL AUTO_INCREMENT,
  `sdtNhanVien` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `timeStart` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `statusStart` enum('SUCCESS','FAILED') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `isDeepfakeDetectedStart` tinyint(1) NULL DEFAULT 0,
  `deepfakeScoreStart` float NULL DEFAULT NULL,
  `photoCapturedStart` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `timeEnd` timestamp NULL DEFAULT NULL,
  `statusEnd` enum('SUCCESS','FAILED') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `isDeepfakeDetectedEnd` tinyint(1) NULL DEFAULT NULL,
  `deepfakeScoreEnd` float NULL DEFAULT NULL,
  `photoCapturedEnd` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `LinkVideoDeepFakeStart` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `LinkVideoDeepFakeEnd` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL,
  `StatusDeepFakeStart` enum('SUCCESS','FAILED','NOT DEEPFAKE') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `StatusDeepFakeEnd` enum('SUCCESS','FAILED','NOT DEEPFAKE') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  PRIMARY KEY (`logId`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 25 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of attendancelogs
-- ----------------------------
INSERT INTO `attendancelogs` VALUES (23, '0333657671', '2025-02-08 00:54:49', 'FAILED', 0, 0, '/static/images/data/0333657671_20250208005445358380.jpg', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL);
INSERT INTO `attendancelogs` VALUES (24, '111111111', '2025-02-08 01:13:11', 'FAILED', 0, 0.296013, '/static/images/data/111111111_20250208011304241208.jpg', NULL, NULL, NULL, NULL, NULL, '/static/images/data/111111111_20250208011304242204.mp4', NULL, 'SUCCESS', NULL);

-- ----------------------------
-- Table structure for departments
-- ----------------------------
DROP TABLE IF EXISTS `departments`;
CREATE TABLE `departments`  (
  `department_id` int NOT NULL AUTO_INCREMENT,
  `department_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`department_id`) USING BTREE,
  UNIQUE INDEX `department_name`(`department_name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of departments
-- ----------------------------
INSERT INTO `departments` VALUES (1, 'Phòng Kế Toán', '2025-01-16 18:51:20');
INSERT INTO `departments` VALUES (2, 'Phòng IT', '2025-01-16 18:51:20');
INSERT INTO `departments` VALUES (3, 'Phòng Nhân Sự', '2025-01-16 18:51:20');
INSERT INTO `departments` VALUES (4, 'Phòng Sale', '2025-01-16 18:51:20');

-- ----------------------------
-- Table structure for employees
-- ----------------------------
DROP TABLE IF EXISTS `employees`;
CREATE TABLE `employees`  (
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
  CONSTRAINT `Employees_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `departments` (`department_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 10 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Records of employees
-- ----------------------------
INSERT INTO `employees` VALUES (1, 'admin', 'admin@gmail.com', '111111111', 'pass', 'admin', '/static/images/key-person.png', 'admin', '2025-01-18 06:08:20', b'1', 1);
INSERT INTO `employees` VALUES (7, 'Trần Văn B', '1@gmail.com', '0333657671', 'pass', 'Dev', '/static/images/1_0333657671.jpg', 'user', '2025-01-18 06:16:23', b'1', 2);
INSERT INTO `employees` VALUES (8, 'Trần Văn Chú', '2@gmail.com', '033656572', 'pass', 'dev', '/static/images/data/2_033656572.jpg', 'user', '2025-01-18 06:24:41', b'1', 1);
INSERT INTO `employees` VALUES (9, 'thành', 'a3@gmail.com', '033657673', 'pass', 'dev', '/static/images/data/a3_033657673.jpg', 'user', '2025-01-18 06:30:20', b'1', 1);

SET FOREIGN_KEY_CHECKS = 1;
