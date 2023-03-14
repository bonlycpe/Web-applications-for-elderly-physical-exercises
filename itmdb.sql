-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 14, 2023 at 05:30 PM
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
(1, 1, 2, 'ยืดเส้นยืดสายกายใจ'),
(2, 3, 4, 'เบาสบายกายขยับ');

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
(9, 2, 1, 26.7366, '2023-03-14');

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
(1, 'แกว่งแขน'),
(2, 'ย่ำเท้างอขา'),
(3, 'กางแขนยกมือ'),
(4, 'กำหมัดยกขา');

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
(2, 2, 2);

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
(2, 'admin', 'admin', 'admin', 'admin', 'admin', 31, 160),
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
  MODIFY `historyUserCourseID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `posture`
--
ALTER TABLE `posture`
  MODIFY `postureID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `usercourse`
--
ALTER TABLE `usercourse`
  MODIFY `userCourseID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

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
