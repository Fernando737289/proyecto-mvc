-- phpMyAdmin SQL Dump
-- version 5.2.3
-- https://www.phpmyadmin.net/
--
-- Servidor: mysql
-- Tiempo de generación: 15-06-2026 a las 21:10:33
-- Versión del servidor: 8.0.46
-- Versión de PHP: 8.3.26

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

DROP DATABASE IF EXISTS backTarjetaVecino;
CREATE DATABASE backTarjetaVecino
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE backTarjetaVecino;

--
-- Base de datos: `backTarjetaVecino`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auditoria`
--

CREATE TABLE `auditoria` (
  `id_auditoria` int NOT NULL,
  `tabla_afectada` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `accion_realizada` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `usuario_accion` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_accion` datetime NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `beneficios`
--

CREATE TABLE `beneficios` (
  `id_beneficio` int NOT NULL,
  `nombre` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `tipo_descuento` enum('porcentaje','monto_fijo','2x1') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `valor_descuento` decimal(10,2) DEFAULT NULL,
  `stock` int NOT NULL DEFAULT '0',
  `fecha_inicio` date DEFAULT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  `comercio` varchar(150) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado` enum('activo','inactivo') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'activo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `beneficios`
--

INSERT INTO `beneficios` (`id_beneficio`, `nombre`, `descripcion`, `tipo_descuento`, `valor_descuento`, `stock`, `fecha_inicio`, `fecha_vencimiento`, `comercio`, `estado`) VALUES
(1, 'Piscina Municipal', '50% de descuento en el ingreso a la piscina municipal', 'porcentaje', 50.00, 499, '2026-06-01', '2026-12-31', 'Municipalidad de San Bernardo', 'activo'),
(2, 'Talleres Culturales', 'Acceso gratuito a talleres de pintura, teatro y musica', 'monto_fijo', 10000.00, 198, '2026-06-01', '2026-12-31', 'Centro Cultural Municipal', 'activo'),
(3, 'Libreria Escolar', 'Descuento para la compra de utiles y libros escolares', 'porcentaje', 15.00, 299, '2026-06-01', '2026-12-31', 'Libreria Educativa San Bernardo', 'activo'),
(4, 'Farmacia Municipal', '20% de descuento en medicamentos seleccionados', 'porcentaje', 20.00, 1000, '2026-06-01', '2026-12-31', 'Farmacia Municipal San Bernardo', 'activo'),
(5, 'Cine Vecino', 'Promocion 2x1 en entradas de cine', '2x1', 0.00, 400, '2026-06-01', '2026-12-31', 'Cine San Bernardo', 'activo'),
(6, 'Actividades Deportivas', 'Descuento en talleres y actividades deportivas municipales', 'porcentaje', 30.00, 250, '2026-06-01', '2026-12-31', 'Departamento de Deportes', 'activo');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `historial_beneficios`
--

CREATE TABLE `historial_beneficios` (
  `id_historial` int NOT NULL,
  `id_persona` int NOT NULL,
  `id_beneficio` int NOT NULL,
  `codigo_canje` varchar(50) NOT NULL,
  `fecha_uso` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `historial_beneficios`
--

INSERT INTO `historial_beneficios` (`id_historial`, `id_persona`, `id_beneficio`, `fecha_uso`) VALUES
(1, 13, 1, '2026-06-15 20:06:59'),
(10, 13, 2, '2026-06-15 21:04:34'),
(12, 13, 3, '2026-06-15 21:09:49');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `persona`
--

CREATE TABLE `persona` (
  `id_persona` int NOT NULL,
  `rut` varchar(12) COLLATE utf8mb4_unicode_ci NOT NULL,
  `serial_number` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombres` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `apellidos` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `direccion` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `numero_direccion` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `telefono` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `estado` enum('activo','inactivo') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'activo',
  `fecha_creacion` datetime NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `persona`
--

INSERT INTO `persona` (`id_persona`, `rut`, `serial_number`, `nombres`, `apellidos`, `direccion`, `numero_direccion`, `telefono`, `email`, `fecha_nacimiento`, `estado`, `fecha_creacion`) VALUES
(11, '14187947-2', 'gAAAAABqKO64N3o5wadk1JP9zRU-_DBuEC7WTAZGvv6G3kNI4loEi0z0bNyYYwNgv2vG7yWFLbE4iWI6RS4n9zG-IH75iH8lqA==', 'Francisco', 'Baez', 'string', 'string', 'string', 'user@example.com', '2026-06-10', 'activo', '2026-06-10 04:57:28'),
(13, '21817151-6', 'gAAAAABqKO8Z_nE3zmptJOgoF-VIYvSddXcsMJb_MlIyH6hTgMZV62QFyWKELIlirApZHzvcfyQqkWxkEVB2esN8ihiOXRD81w==', 'Fernando', 'Maturana', 'string', 'string', 'string', 'user@example.com', '2026-06-10', 'activo', '2026-06-10 04:59:05');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tarjeta`
--

CREATE TABLE `tarjeta` (
  `id_tarjeta` int NOT NULL,
  `id_persona` int NOT NULL,
  `numero_tarjeta` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `codigo_qr` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_emision` date NOT NULL,
  `fecha_vencimiento` date NOT NULL,
  `estado` enum('activa','bloqueada','vencida') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'activa'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `tarjeta`
--

INSERT INTO `tarjeta` (`id_tarjeta`, `id_persona`, `numero_tarjeta`, `codigo_qr`, `fecha_emision`, `fecha_vencimiento`, `estado`) VALUES
(9, 13, '711861', 'iVBORw0KGgoAAAANSUhEUgAAAZoAAAGaAQAAAAAefbjOAAAC90lEQVR4nO2cwY3bMBBF30QC9igDKcClUB2kpi0pHUilpIAFpKMBCj8HkpIc55BdB5YtDQ8+mHwQCQ/+DD8pm/h06799ngGHHHLIIYcccmifkOVWY3YCGGusHc2AyWAsA9pNpufQ46EgSRpAGgCaCP1ZsnassZZKkqRr6HHTc+jx0JgFwFomS0IRhsnUNTENMLN6u+k5tB3Un0DdaKZ3exOM9T9AX3qSQ08J3f7eYw1BU200H0bohP2XJzn0GlCJiEbACOp/DBhUAibUWxXFCGsn68nX5NA9EOuKkUqE4W8fZUCQpO7J1+TQPVDSiEUA1J8vJojQny+Wdh1JQbaYnkMPh1YaIQ2Vln0oNJK6JqKukUgK4hpxDCiFRX++mN5PpSv8qoHxTTCa5SjZZHoObaARjVLNkFpHJXWzRsyS4Rqxf2gVEZIiBKXCIf36JUoi0ERyvDz5mhy6B2ItCkkZIupSR1zVFsCsIE++JofugUpENFJWgSEfbuSEUXrTh0fE7qGcNYIihKFsOHLWKBGhpdcjYu/QVWVZ8sdSY5Lcy5RJPGscAVqrwPJd10SSXTlnkuxeekTsHVqddGVfcvweLQzT9bAqWrIwv/4kh14DKhoxVCVDzG1JHUGeNQ4D/bmbKC7EstfIwZA7PCL2DuWsEYapBuooxhNirGIysPu2EjQfpt7mxPLka3LoHqjsPq83F7NQpLPPJBl+0nUIaF1HrHJFKSty1pgPQD0idg9de5azKwmze7kuLz0i9g/NnmVJHSspaIphlZprxCGg2aFSqSOarBHFxc7KgN+YORK0vNOlLt3FVr6Y358g388eJkuh8hprcuguKKTykqQM1jIlf9Lacq4BVLJ2m+k5tMHuk2xSdlD8yeF2tGeNw0HWAtBcjP6cq81yfSpfpXm5NTn0mXbzTlf4mU+6LAyg/lShvq2B8fT46Tn0cGi1+yyXZbJDVY7Ei13pu89jQDfvdM1OZW4rU8LPPo8Amf8zmUMOOeSQQw459EXoN8wm5x5CgsRJAAAAAElFTkSuQmCC', '2026-06-13', '2027-06-13', 'activa');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario`
--

CREATE TABLE `usuario` (
  `id_usuario` int NOT NULL,
  `username` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `rol` enum('admin','funcionario') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'funcionario',
  `estado` enum('activo','inactivo') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'activo',
  `fecha_creacion` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Volcado de datos para la tabla `usuario`
--

INSERT INTO `usuario` (`id_usuario`, `username`, `password_hash`, `rol`, `estado`, `fecha_creacion`, `email`) VALUES
(3, 'admin', '$2b$14$25h50/7DZyI9wQtkIFGSHeR/Nih03H3NYsP931h9.NUC54umSea4S', 'admin', 'activo', '2026-06-09 07:58:38', 'user@example.com'),
(4, 'funcionario 1', '$2b$14$smtMzkXN8WlyNokhth3Dxu.PTR0SYMlNO6v5R0EdSB2rps9VGz8YW', 'funcionario', 'activo', '2026-06-11 19:07:41', 'funcionario@example.com');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `auditoria`
--
ALTER TABLE `auditoria`
  ADD PRIMARY KEY (`id_auditoria`);

--
-- Indices de la tabla `beneficios`
--
ALTER TABLE `beneficios`
  ADD PRIMARY KEY (`id_beneficio`);

--
-- Indices de la tabla `historial_beneficios`
--
ALTER TABLE `historial_beneficios`
  ADD PRIMARY KEY (`id_historial`),
  ADD KEY `fk_historial_persona` (`id_persona`),
  ADD KEY `fk_historial_beneficio` (`id_beneficio`);

--
-- Indices de la tabla `persona`
--
ALTER TABLE `persona`
  ADD PRIMARY KEY (`id_persona`),
  ADD UNIQUE KEY `uk_persona_rut` (`rut`);

--
-- Indices de la tabla `tarjeta`
--
ALTER TABLE `tarjeta`
  ADD PRIMARY KEY (`id_tarjeta`),
  ADD UNIQUE KEY `uk_tarjeta_persona` (`id_persona`),
  ADD UNIQUE KEY `uk_tarjeta_numero` (`numero_tarjeta`);

--
-- Indices de la tabla `usuario`
--
ALTER TABLE `usuario`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `uk_usuario_username` (`username`),
  ADD UNIQUE KEY `uk_usuario_email` (`email`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `auditoria`
--
ALTER TABLE `auditoria`
  MODIFY `id_auditoria` int NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `beneficios`
--
ALTER TABLE `beneficios`
  MODIFY `id_beneficio` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT de la tabla `historial_beneficios`
--
ALTER TABLE `historial_beneficios`
  MODIFY `id_historial` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT de la tabla `persona`
--
ALTER TABLE `persona`
  MODIFY `id_persona` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT de la tabla `tarjeta`
--
ALTER TABLE `tarjeta`
  MODIFY `id_tarjeta` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT de la tabla `usuario`
--
ALTER TABLE `usuario`
  MODIFY `id_usuario` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `historial_beneficios`
--
ALTER TABLE `historial_beneficios`
  ADD CONSTRAINT `fk_historial_beneficio` FOREIGN KEY (`id_beneficio`) REFERENCES `beneficios` (`id_beneficio`),
  ADD CONSTRAINT `fk_historial_persona` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`);

--
-- Filtros para la tabla `tarjeta`
--
ALTER TABLE `tarjeta`
  ADD CONSTRAINT `fk_tarjeta_persona` FOREIGN KEY (`id_persona`) REFERENCES `persona` (`id_persona`) ON DELETE RESTRICT ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
