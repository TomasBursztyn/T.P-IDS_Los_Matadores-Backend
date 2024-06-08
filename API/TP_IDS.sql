-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: localhost
-- Tiempo de generación: 09-06-2024 a las 01:29:20
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `TP_IDS`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tabla_habitaciones`
--

CREATE TABLE `tabla_habitaciones` (
  `id_habitacion` int(3) NOT NULL,
  `tipo_habitacion` varchar(50) NOT NULL,
  `precio_por_noche` int(6) NOT NULL,
  `cantidad_personas` int(2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tabla_habitaciones`
--

INSERT INTO `tabla_habitaciones` (`id_habitacion`, `tipo_habitacion`, `precio_por_noche`, `cantidad_personas`) VALUES
(2, 'standard', 40, 4),
(3, 'standard', 40, 4),
(4, 'standard', 40, 4),
(5, 'standard', 40, 4),
(6, 'standard', 40, 4),
(7, 'suite premium', 70, 6),
(8, 'suite premium', 70, 6),
(9, 'suite premium', 70, 6),
(10, 'suite premium', 70, 6),
(11, 'suite premium', 70, 6),
(12, 'suite flotante', 100, 2),
(13, 'suite flotante', 100, 2),
(14, 'suite flotante', 100, 2),
(15, 'suite flotante', 100, 2),
(16, 'suite flotante', 100, 2);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tabla_personas`
--

CREATE TABLE `tabla_personas` (
  `id_persona` int(5) NOT NULL,
  `nombre_persona` varchar(50) NOT NULL,
  `telefono_persona` int(15) NOT NULL,
  `email_persona` varchar(50) NOT NULL,
  `dni_persona` int(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `tabla_personas`
--

INSERT INTO `tabla_personas` (`id_persona`, `nombre_persona`, `telefono_persona`, `email_persona`, `dni_persona`) VALUES
(5, 'julian', 1163665, 'jdjkajsdjl', 428394);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tabla_reservas`
--

CREATE TABLE `tabla_reservas` (
  `id_reserva` int(5) NOT NULL,
  `id_habitaciones` int(3) NOT NULL,
  `id_personas` int(5) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_salida` date NOT NULL,
  `total_a_pagar` int(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `tabla_habitaciones`
--
ALTER TABLE `tabla_habitaciones`
  ADD PRIMARY KEY (`id_habitacion`);

--
-- Indices de la tabla `tabla_personas`
--
ALTER TABLE `tabla_personas`
  ADD PRIMARY KEY (`id_persona`);

--
-- Indices de la tabla `tabla_reservas`
--
ALTER TABLE `tabla_reservas`
  ADD PRIMARY KEY (`id_reserva`),
  ADD KEY `fk_id_persona` (`id_personas`) USING BTREE,
  ADD KEY `fk_id_habitacion` (`id_habitaciones`) USING BTREE;

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `tabla_habitaciones`
--
ALTER TABLE `tabla_habitaciones`
  MODIFY `id_habitacion` int(3) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT de la tabla `tabla_personas`
--
ALTER TABLE `tabla_personas`
  MODIFY `id_persona` int(5) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT de la tabla `tabla_reservas`
--
ALTER TABLE `tabla_reservas`
  MODIFY `id_reserva` int(5) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `tabla_reservas`
--
ALTER TABLE `tabla_reservas`
  ADD CONSTRAINT `fk_padre` FOREIGN KEY (`id_personas`) REFERENCES `tabla_personas` (`id_persona`),
  ADD CONSTRAINT `junior` FOREIGN KEY (`id_habitaciones`) REFERENCES `tabla_habitaciones` (`id_habitacion`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
