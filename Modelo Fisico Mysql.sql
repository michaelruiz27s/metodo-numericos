-- Se crea la base de datos
Create Database IF Not Exists Metodos_Numericos;

Use Metodos_Numericos
-- Se crea la tabla Metodo_Bisección
Create TABLE metodo_biseccion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ejercicio int,
    iteracion INT,
   xa double,
    xb double,
    fxa double,
    fxb double,
    xr double,
    fxr double,
    ea double
);
CREATE TABLE metodo_falsa_posicion (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    Ejercicio INT NOT NULL,
    Iteracion INT NOT NULL,
    Xa double,
    Xb double,
    FXa double,
    FXb double,
    Xr double,
    FXr double,
    Ea double
);
Create table metodo_punto_fijo(
	Id INT AUTO_INCREMENT PRIMARY KEY,
    Ejercicio INT NOT NULL,
    Iteracion INT NOT NULL,
    Xi double,
    GXi double,
    Ea double
    );
CREATE TABLE metodo_newton_raphson (
    ejercicio INT,
    iteracion INT,
    xi DOUBLE,
    fxi DOUBLE,
    dfxi DOUBLE,
    xi1 DOUBLE,
    ea DOUBLE
);
CREATE TABLE metodo_secante (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ejercicio INT NOT NULL,
    iteracion INT NOT NULL,
    xi_1 DOUBLE,
    xi DOUBLE,
    fxi_1 DOUBLE,
    fxi DOUBLE,
    xi_t DOUBLE,
    ea DOUBLE
);
CREATE TABLE metodo_newton_sistemas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ejercicio INT NOT NULL,
    iteracion INT NOT NULL,
    
    -- Valores de X
    x DOUBLE,
    y DOUBLE,

    -- Valores de F(X)
    fx DOUBLE,
    fy DOUBLE,

    -- Jacobiano
    j11 DOUBLE,
    j12 DOUBLE,
    j21 DOUBLE,
    j22 DOUBLE,

    -- Inversa de Jacobiano
    inv_j11 DOUBLE,
    inv_j12 DOUBLE,
    inv_j21 DOUBLE,
    inv_j22 DOUBLE,

    -- Delta X
    delta_x DOUBLE,
    delta_y DOUBLE,

    -- Error
    e1 DOUBLE,
    e2 DOUBLE
);







Drop table metodo_newton_sistemas
DROP DATABASE Metodos_Numericos;
