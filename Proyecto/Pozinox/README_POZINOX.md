# Pozinox - Sistema de Gestión para Tienda de Aceros

## 🏗️ Descripción
Sistema completo de gestión para tienda de aceros con módulos de:
- **Tienda**: Catálogo de productos, ventas, clientes
- **Inventario**: Control de stock, proveedores, movimientos
- **Usuarios**: Gestión de usuarios, roles, notificaciones

## 📋 Requisitos Previos
- Python 3.8+
- MySQL 8.0+
- pip (gestor de paquetes de Python)

## 🚀 Instalación

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar MySQL
- Crear base de datos: `CREATE DATABASE pozinox_db;`
- Actualizar configuración en `Pozinox/settings.py`

### 3. Configurar variables de entorno (opcional)
```bash
# Copiar archivo de ejemplo
cp .env.example .env
# Editar .env con tus configuraciones
```

### 4. Ejecutar migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear superusuario
```bash
python manage.py createsuperuser
```

### 6. Ejecutar servidor
```bash
python manage.py runserver
```

## 📁 Estructura del Proyecto
```
Pozinox/
├── apps/
│   ├── tienda/          # Gestión de productos y ventas
│   ├── inventario/      # Control de stock y proveedores
│   └── usuarios/        # Gestión de usuarios y configuraciones
├── templates/           # Plantillas HTML
├── static/             # Archivos estáticos (CSS, JS, imágenes)
├── media/              # Archivos subidos por usuarios
└── Pozinox/            # Configuración del proyecto
```

## 🎯 Características Principales

### Tienda
- Catálogo de productos de acero
- Gestión de clientes
- Sistema de pedidos
- Categorización por tipo de acero

### Inventario
- Control de stock en tiempo real
- Gestión de proveedores
- Movimientos de inventario
- Alertas automáticas de stock bajo

### Usuarios
- Sistema de roles y permisos
- Perfiles de usuario personalizables
- Logs de actividad
- Sistema de notificaciones

## 🔧 Configuración de Base de Datos

### MySQL
```sql
CREATE DATABASE pozinox_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'pozinox_user'@'localhost' IDENTIFIED BY 'tu_contraseña';
GRANT ALL PRIVILEGES ON pozinox_db.* TO 'pozinox_user'@'localhost';
FLUSH PRIVILEGES;
```

## 📞 Soporte
Para dudas o problemas, contactar al equipo de desarrollo.
