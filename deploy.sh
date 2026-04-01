#!/bin/bash
set -e

# ==========================================
#  爱保尼阀门维修系统 - 一键部署脚本
#  支持 Ubuntu/Debian 和 CentOS/RHEL
# ==========================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
APP_NAME="aibaoni"
APP_DIR="/opt/aibaoni"
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"
DEPLOY_DIR="$APP_DIR/deploy"
LOG_DIR="/var/log/$APP_NAME"
REQUIRED_NODE_VERSION="20"

# 输出函数
print_header() {
    echo -e "\n${BLUE}===========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}===========================================${NC}\n"
}

print_step() {
    echo -e "${YELLOW}>>> $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# 错误处理
error_exit() {
    print_error "$1"
    exit 1
}

# 检查 root 权限
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error_exit "请使用 root 权限运行此脚本 (sudo ./deploy.sh)"
    fi
    print_success "root 权限检查通过"
}

# 检测操作系统
detect_os() {
    print_step "检测操作系统..."
    
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
        VERSION=$VERSION_ID
    elif [ -f /etc/redhat-release ]; then
        OS="centos"
    elif [ -f /etc/debian_version ]; then
        OS="debian"
    else
        error_exit "不支持的操作系统"
    fi
    
    case $OS in
        ubuntu|debian)
            PKG_MANAGER="apt"
            print_success "检测到 $OS $VERSION (Debian/Ubuntu 系列)"
            ;;
        centos|rhel|rocky|almalinux)
            PKG_MANAGER="yum"
            if command -v dnf &> /dev/null; then
                PKG_MANAGER="dnf"
            fi
            print_success "检测到 $OS $VERSION (RHEL 系列)"
            ;;
        *)
            error_exit "不支持的操作系统: $OS"
            ;;
    esac
}

# 安装系统依赖
install_dependencies() {
    print_step "安装系统依赖..."
    
    if [ "$PKG_MANAGER" = "apt" ]; then
        apt update -qq
        apt install -y python3 python3-venv python3-pip nginx curl
        print_success "Python3, Nginx 安装完成"
    else
        $PKG_MANAGER install -y python3 python3-pip nginx curl
        print_success "Python3, Nginx 安装完成"
    fi
}

# 检查并安装 Node.js
install_nodejs() {
    print_step "检查 Node.js 版本..."
    
    NEED_INSTALL=false
    
    if command -v node &> /dev/null; then
        CURRENT_VERSION=$(node -v | sed 's/v//' | cut -d. -f1)
        print_info "当前 Node.js 版本: $(node -v)"
        
        if [ "$CURRENT_VERSION" -lt "$REQUIRED_NODE_VERSION" ]; then
            print_info "Node.js 版本需要 >= 20，将安装新版本..."
            NEED_INSTALL=true
        else
            print_success "Node.js 版本满足要求"
        fi
    else
        print_info "未检测到 Node.js，将安装 Node.js 20..."
        NEED_INSTALL=true
    fi
    
    if [ "$NEED_INSTALL" = true ]; then
        print_step "通过 NodeSource 安装 Node.js 20..."
        
        if [ "$PKG_MANAGER" = "apt" ]; then
            # Ubuntu/Debian
            curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
            apt install -y nodejs
        else
            # CentOS/RHEL
            curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
            $PKG_MANAGER install -y nodejs
        fi
        
        print_success "Node.js $(node -v) 安装完成"
    fi
}

# 创建目录结构
create_directories() {
    print_step "创建应用目录..."
    
    mkdir -p "$APP_DIR"
    mkdir -p "$LOG_DIR"
    
    print_success "目录创建完成: $APP_DIR, $LOG_DIR"
}

# 复制项目文件
copy_project_files() {
    print_step "复制项目文件..."
    
    # 获取脚本所在目录（即项目根目录）
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    if [ "$SCRIPT_DIR" = "$APP_DIR" ]; then
        print_info "已在目标目录，跳过复制"
    else
        # 复制项目文件，排除 node_modules 和 venv
        rsync -av --delete \
            --exclude 'node_modules' \
            --exclude 'venv' \
            --exclude '.git' \
            --exclude '__pycache__' \
            --exclude '*.pyc' \
            "$SCRIPT_DIR/" "$APP_DIR/"
        
        print_success "项目文件复制完成"
    fi
}

# 部署后端
deploy_backend() {
    print_step "部署后端服务..."
    
    cd "$BACKEND_DIR"
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        print_info "创建 Python 虚拟环境..."
        python3 -m venv venv
    fi
    
    # 激活虚拟环境并安装依赖
    print_info "安装 Python 依赖..."
    source venv/bin/activate
    pip install --upgrade pip -q
    pip install -r requirements.txt -q
    pip install gunicorn -q
    deactivate
    
    # 设置权限
    chown -R www-data:www-data "$BACKEND_DIR"
    chmod -R 755 "$BACKEND_DIR"
    
    # 确保日志目录权限
    chown -R www-data:www-data "$LOG_DIR"
    chmod -R 755 "$LOG_DIR"
    
    print_success "后端部署完成"
}

# 部署前端
deploy_frontend() {
    print_step "部署前端服务..."
    
    cd "$FRONTEND_DIR"
    
    # 安装依赖
    print_info "安装前端依赖 (npm install)..."
    npm install --silent
    
    # 构建
    print_info "构建前端项目 (npm run build)..."
    npm run build
    
    # 设置权限
    chown -R www-data:www-data "$FRONTEND_DIR"
    chmod -R 755 "$FRONTEND_DIR"
    
    print_success "前端部署完成"
}

# 配置 Nginx
configure_nginx() {
    print_step "配置 Nginx..."
    
    NGINX_AVAILABLE="/etc/nginx/sites-available"
    NGINX_ENABLED="/etc/nginx/sites-enabled"
    NGINX_CONF_D="/etc/nginx/conf.d"
    
    # 判断 Nginx 配置目录结构
    if [ -d "$NGINX_AVAILABLE" ]; then
        # Debian/Ubuntu 风格
        cp "$DEPLOY_DIR/nginx.conf" "$NGINX_AVAILABLE/$APP_NAME"
        
        # 创建软链接
        if [ -L "$NGINX_ENABLED/$APP_NAME" ]; then
            rm "$NGINX_ENABLED/$APP_NAME"
        fi
        ln -s "$NGINX_AVAILABLE/$APP_NAME" "$NGINX_ENABLED/$APP_NAME"
        
        # 删除默认配置
        if [ -L "$NGINX_ENABLED/default" ]; then
            rm "$NGINX_ENABLED/default"
            print_info "已删除默认 Nginx 配置"
        fi
    else
        # CentOS/RHEL 风格
        cp "$DEPLOY_DIR/nginx.conf" "$NGINX_CONF_D/$APP_NAME.conf"
    fi
    
    # 测试 Nginx 配置
    print_info "测试 Nginx 配置..."
    nginx -t || error_exit "Nginx 配置测试失败"
    
    # 重载 Nginx
    systemctl reload nginx
    systemctl enable nginx
    
    print_success "Nginx 配置完成"
}

# 配置 Systemd 服务
configure_systemd() {
    print_step "配置 Systemd 服务..."
    
    # 复制服务文件
    cp "$DEPLOY_DIR/aibaoni.service" "/etc/systemd/system/$APP_NAME.service"
    
    # 重新加载 systemd
    systemctl daemon-reload
    
    # 启用并启动服务
    systemctl enable "$APP_NAME"
    systemctl restart "$APP_NAME"
    
    # 等待服务启动
    sleep 2
    
    # 检查服务状态
    if systemctl is-active --quiet "$APP_NAME"; then
        print_success "Systemd 服务配置完成并已启动"
    else
        print_error "服务启动失败，请检查日志: journalctl -u $APP_NAME"
    fi
}

# 获取服务器 IP
get_server_ip() {
    # 尝试获取公网 IP
    PUBLIC_IP=$(curl -s --connect-timeout 3 ifconfig.me 2>/dev/null || echo "")
    
    # 获取内网 IP
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    
    if [ -n "$PUBLIC_IP" ]; then
        echo "$PUBLIC_IP"
    else
        echo "$LOCAL_IP"
    fi
}

# 输出部署结果
print_result() {
    print_header "部署完成"
    
    echo -e "${GREEN}服务状态:${NC}"
    echo "-------------------------------------------"
    
    # Nginx 状态
    if systemctl is-active --quiet nginx; then
        echo -e "  Nginx:    ${GREEN}运行中${NC}"
    else
        echo -e "  Nginx:    ${RED}未运行${NC}"
    fi
    
    # 后端服务状态
    if systemctl is-active --quiet "$APP_NAME"; then
        echo -e "  后端服务: ${GREEN}运行中${NC}"
    else
        echo -e "  后端服务: ${RED}未运行${NC}"
    fi
    
    echo ""
    echo -e "${GREEN}访问地址:${NC}"
    echo "-------------------------------------------"
    SERVER_IP=$(get_server_ip)
    echo -e "  http://$SERVER_IP"
    echo ""
    
    echo -e "${GREEN}常用命令:${NC}"
    echo "-------------------------------------------"
    echo "  查看服务状态:   systemctl status $APP_NAME"
    echo "  重启后端服务:   systemctl restart $APP_NAME"
    echo "  查看后端日志:   journalctl -u $APP_NAME -f"
    echo "  查看访问日志:   tail -f $LOG_DIR/access.log"
    echo "  查看错误日志:   tail -f $LOG_DIR/error.log"
    echo "  重载 Nginx:     systemctl reload nginx"
    echo ""
    
    echo -e "${YELLOW}注意事项:${NC}"
    echo "-------------------------------------------"
    echo "  1. 如需配置域名，请修改 /etc/nginx/sites-available/$APP_NAME"
    echo "  2. 如需配置 HTTPS，建议使用 certbot"
    echo "  3. 防火墙需开放 80 端口: ufw allow 80/tcp"
    echo ""
}

# 主函数
main() {
    print_header "爱保尼阀门维修系统 - 一键部署脚本"
    
    check_root
    detect_os
    install_dependencies
    install_nodejs
    create_directories
    copy_project_files
    deploy_backend
    deploy_frontend
    configure_nginx
    configure_systemd
    print_result
    
    print_success "部署完成！"
}

# 执行主函数
main "$@"
