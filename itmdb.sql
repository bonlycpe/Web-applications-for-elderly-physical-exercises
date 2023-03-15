-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 15, 2023 at 06:23 PM
-- Server version: 10.4.25-MariaDB
-- PHP Version: 8.1.10

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `itmdb`
--

-- --------------------------------------------------------

--
-- Table structure for table `course`
--

CREATE TABLE `course` (
  `courseID` int(11) NOT NULL,
  `posture1ID` int(10) NOT NULL,
  `posture2ID` int(10) NOT NULL,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `course`
--

INSERT INTO `course` (`courseID`, `posture1ID`, `posture2ID`, `name`) VALUES
(1, 1, 2, 'เบาสบายกายขยับ'),
(2, 3, 4, 'กำหมัดสลัดเหงื่อ');

-- --------------------------------------------------------

--
-- Table structure for table `historyusercourse`
--

CREATE TABLE `historyusercourse` (
  `historyUserCourseID` int(11) NOT NULL,
  `userCourseID` int(11) NOT NULL,
  `score` int(10) NOT NULL,
  `timer` float NOT NULL COMMENT 'Seconds',
  `date` date NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `historyusercourse`
--

INSERT INTO `historyusercourse` (`historyUserCourseID`, `userCourseID`, `score`, `timer`, `date`) VALUES
(1, 1, 1, 22, '2023-03-10'),
(2, 1, 1, 24, '2023-03-10'),
(3, 1, 2, 22, '2023-03-10'),
(4, 1, 3, 34, '2023-03-10'),
(5, 1, 1, 66, '2023-03-10'),
(7, 1, 3, 123.1, '2023-03-14'),
(8, 2, 1, 69, '2023-03-14'),
(9, 2, 1, 26.7366, '2023-03-14'),
(10, 28, 100, 62.8045, '2023-03-15'),
(11, 28, 100, 63.6085, '2023-03-15'),
(12, 33, 100, 120.54, '2023-03-15'),
(13, 33, 0, 0, '2023-03-15'),
(14, 41, 100, 93.074, '2023-03-16'),
(15, 44, 100, 95.5759, '2023-03-16');

-- --------------------------------------------------------

--
-- Table structure for table `posture`
--

CREATE TABLE `posture` (
  `postureID` int(11) NOT NULL,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `posture`
--

INSERT INTO `posture` (`postureID`, `name`) VALUES
(1, 'ยกแขนยกขา '),
(2, 'ย่ำเท้างอขา'),
(3, 'กำหมัดก้าวเท้า'),
(4, 'ยืดอกก้าวหลัง');

-- --------------------------------------------------------

--
-- Table structure for table `usercourse`
--

CREATE TABLE `usercourse` (
  `userCourseID` int(11) NOT NULL,
  `userID` int(11) NOT NULL,
  `courseID` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `usercourse`
--

INSERT INTO `usercourse` (`userCourseID`, `userID`, `courseID`) VALUES
(1, 2, 1),
(2, 2, 2),
(3, 2, 1),
(4, 2, 1),
(5, 2, 1),
(6, 2, 1),
(7, 2, 1),
(8, 2, 1),
(9, 2, 2),
(10, 2, 1),
(11, 2, 2),
(12, 2, 1),
(13, 2, 1),
(14, 2, 1),
(15, 2, 2),
(16, 2, 1),
(17, 2, 1),
(18, 2, 2),
(19, 2, 1),
(20, 2, 1),
(21, 2, 2),
(22, 2, 1),
(23, 2, 2),
(24, 2, 1),
(25, 2, 1),
(26, 2, 1),
(27, 2, 1),
(28, 2, 1),
(29, 2, 1),
(30, 2, 1),
(31, 2, 1),
(32, 2, 1),
(33, 2, 1),
(34, 2, 1),
(35, 2, 1),
(36, 2, 1),
(37, 2, 1),
(38, 2, 1),
(39, 2, 1),
(40, 2, 2),
(41, 2, 1),
(42, 2, 1),
(43, 2, 2),
(44, 2, 1),
(45, 2, 1),
(46, 2, 1);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `userID` int(11) NOT NULL,
  `email` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `username` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `surname` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL,
  `age` int(11) NOT NULL,
  `height` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`userID`, `email`, `username`, `password`, `name`, `surname`, `age`, `height`) VALUES
(2, 'admin', 'admin', 'admin', 'admin', 'admin', 75, 160),
(3, 'a1', 'a1', 'a1', 'a1', 'a1', 12, 0),
(4, 'a2', 'a2', 'a2', 'a2', 'a2', 12, 0),
(13, 'peacepeerawat@gmail.com', 'admin', '12345678', 'asdas', 'asdasd', 12, 0);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `course`
--
ALTER TABLE `course`
  ADD PRIMARY KEY (`courseID`),
  ADD UNIQUE KEY `posture1ID_2` (`posture1ID`,`posture2ID`),
  ADD KEY `posture1ID` (`posture1ID`),
  ADD KEY `posture2ID` (`posture2ID`);

--
-- Indexes for table `historyusercourse`
--
ALTER TABLE `historyusercourse`
  ADD PRIMARY KEY (`historyUserCourseID`),
  ADD KEY `useractivityID` (`userCourseID`);

--
-- Indexes for table `posture`
--
ALTER TABLE `posture`
  ADD PRIMARY KEY (`postureID`);

--
-- Indexes for table `usercourse`
--
ALTER TABLE `usercourse`
  ADD PRIMARY KEY (`userCourseID`),
  ADD KEY `userID` (`userID`),
  ADD KEY `activityID` (`courseID`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`userID`),
  ADD UNIQUE KEY `email` (`email`,`username`),
  ADD UNIQUE KEY `email_2` (`email`,`username`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `course`
--
ALTER TABLE `course`
  MODIFY `courseID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `historyusercourse`
--
ALTER TABLE `historyusercourse`
  MODIFY `historyUserCourseID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `posture`
--
ALTER TABLE `posture`
  MODIFY `postureID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `usercourse`
--
ALTER TABLE `usercourse`
  MODIFY `userCourseID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=47;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `userID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `course`
--
ALTER TABLE `course`
  ADD CONSTRAINT `course_ibfk_1` FOREIGN KEY (`posture1ID`) REFERENCES `posture` (`postureID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `course_ibfk_2` FOREIGN KEY (`posture2ID`) REFERENCES `posture` (`postureID`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `historyusercourse`
--
ALTER TABLE `historyusercourse`
  ADD CONSTRAINT `historyusercourse_ibfk_1` FOREIGN KEY (`userCourseID`) REFERENCES `usercourse` (`userCourseID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `historyusercourse_ibfk_2` FOREIGN KEY (`userCourseID`) REFERENCES `usercourse` (`userCourseID`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `usercourse`
--
ALTER TABLE `usercourse`
  ADD CONSTRAINT `usercourse_ibfk_1` FOREIGN KEY (`userID`) REFERENCES `users` (`userID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `usercourse_ibfk_2` FOREIGN KEY (`courseID`) REFERENCES `course` (`courseID`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
