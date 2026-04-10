#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
卡尔曼滤波（Kalman Filter）实现
用于估计动态系统的状态，处理测量噪声
"""

import numpy as np


class KalmanFilter:
    """
    一维卡尔曼滤波器类

    支持的状态转换模型：
        state_k = F * state_(k-1) + noise
    观测模型：
        z_k = H * state_k + measurement_noise
    """

    def __init__(self, dt=0.1, process_noise_std=0.1, measurement_noise_std=0.05):
        """
        初始化卡尔曼滤波器

        参数:
        dt: 时间步长 (秒)
        process_noise_std: 过程噪声标准差 (过程噪声协方差 Q)
        measurement_noise_std: 测量噪声标准差 (观测噪声协方差 R)
        """
        # 状态转移矩阵 (1x1 对于单变量系统)
        self.F = np.array([[1.0]])
        
        # 观测矩阵 (1x1 对于单变量系统)
        self.H = np.array([[1.0]])
        
        # 过程噪声协方差 Q = process_noise_std^2
        self.Q = np.array([[process_noise_std ** 2]])
        
        # 测量噪声协方差 R = measurement_noise_std^2
        self.R = np.array([[measurement_noise_std ** 2]])
        
        # 初始状态估计 (例如初始位置估计)
        self.x_est = np.array([[0.0]])  # 初始位置
        
        # 初始协方差估计 (对初始估计不确定性的量度)
        self.P = np.array([[process_noise_std ** 2]])
        
        # 用于计算下一状态的中间变量
        self.K = None  # 卡尔曼增益
        self.x_pred = None  # 预测状态
        self.P_pred = None  # 预测协方差

    def predict(self):
        """
        预测步骤：基于状态转移模型预测下一状态
        
        执行:
            x_pred = F * x_est
            P_pred = F * P * F^T + Q
        """
        self.x_pred = np.dot(self.F, self.x_est)
        self.P_pred = np.dot(self.F, np.dot(self.P, self.F.T)) + self.Q

    def update(self, measurement):
        """
        更新步骤：基于测量更新状态估计
        
        执行:
            y = measurement - H * x_pred  (残差)
            K = P_pred * H^T * (H * P_pred * H^T + R)^-1  (卡尔曼增益)
            x_est = x_pred + K * y
            P = (I - K * H) * P_pred
        """
        self.predict()
        
        # 计算残差
        y = measurement - np.dot(self.H, self.x_pred)
        
        # 计算卡尔曼增益
        S = np.dot(self.H, np.dot(self.P_pred, self.H.T)) + self.R
        self.K = np.dot(self.P_pred, self.H.T, np.linalg.inv(S))
        
        # 更新状态估计
        self.x_est = self.x_pred + np.dot(self.K, y)
        
        # 更新协方差
        self.P = np.dot(np.eye(1) - np.dot(self.K, self.H), self.P_pred)

    def reset(self, state=0.0, covariance=1.0):
        """
        重置滤波器状态
        
        参数:
        state: 新的初始状态
        covariance: 新的初始协方差
        """
        self.x_est = np.array([[state]])
        self.P = np.array([[covariance]])

    def filter(self, measurements):
        """
        对一系列测量进行滤波
        
        参数:
        measurements: 测量值的列表或数组
        """
        for measurement in measurements:
            self.update(measurement)
        return self.get_state()

    def get_state(self):
        """
        获取当前状态估计和协方差
        
        返回:
        tuple: (位置估计, 协方差)
        """
        return float(self.x_est[0, 0]), float(self.P[0, 0])


class KalmanFilterMultiDimension:
    """
    多维卡尔曼滤波器类 (适用于更复杂的状态向量)
    
    状态向量示例: [位置, 速度]^T
    """

    def __init__(self, dt=0.1, process_noise_std=0.05, measurement_noise_std=0.05):
        """
        初始化多维卡尔曼滤波器
        
        状态向量: [位置, 速度]
        状态方程:
            x_k = F * x_(k-1) + w
            x_pred[k] = x_pred[k-1] + v * dt
            v_pred[k] = v_pred[k-1]
        观测方程:
            z_k = H * x_k + w
            z_k = position (只观测位置)
        """
        # 状态转移矩阵 F (2x2)
        self.F = np.array([
            [1.0, dt],
            [0.0, 1.0]
        ])
        
        # 观测矩阵 H (1x2) - 只观测位置
        self.H = np.array([
            [1.0, 0.0]
        ])
        
        # 过程噪声协方差 Q (2x2)
        self.Q = np.array([
            [process_noise_std**2, 0.0],
            [0.0, process_noise_std**2]
        ])
        
        # 测量噪声协方差 R (1x1)
        self.R = np.array([[measurement_noise_std**2]])
        
        # 初始状态估计 [位置, 速度]
        self.x_est = np.array([[0.0], [0.0]])
        
        # 初始协方差估计
        self.P = np.array([
            [process_noise_std**2, 0.0],
            [0.0, process_noise_std**2]
        ])

    def predict(self):
        """预测步骤"""
        self.x_pred = np.dot(self.F, self.x_est)
        self.P_pred = np.dot(self.F, np.dot(self.P, self.F.T)) + self.Q

    def update(self, measurement):
        """更新步骤"""
        self.predict()
        
        # 计算残差
        y = measurement - np.dot(self.H, self.x_pred)
        
        # 计算卡尔曼增益
        S = np.dot(self.H, np.dot(self.P_pred, self.H.T)) + self.R
        self.K = np.dot(self.P_pred, self.H.T) / S
        
        # 更新状态估计
        self.x_est = self.x_pred + np.dot(self.K, y)
        
        # 更新协方差
        self.P = np.dot(np.eye(2) - np.dot(self.K, self.H), self.P_pred)

    def reset(self, position=0.0, velocity=0.0, covariance=1.0):
        """重置滤波器状态"""
        self.x_est = np.array([
            [position],
            [velocity]
        ])
        self.P = np.array([
            [covariance, 0.0],
            [0.0, covariance]
        ])

    def get_state(self):
        """获取当前状态估计"""
        return {
            'position': float(self.x_est[0, 0]),
            'velocity': float(self.x_est[1, 0]),
            'covariance': float(np.trace(self.P) / 2)
        }


def test_1d_kalman_filter():
    """测试一维卡尔曼滤波器"""
    print("=" * 60)
    print("测试一维卡尔曼滤波")
    print("=" * 60)
    
    # 创建滤波器
    kf = KalmanFilter(dt=0.1)
    
    # 模拟真实值 (假设物体以 0.5 m/s 匀速运动)
    true_velocity = 0.5
    true_position = 0.0
    
    print(f"\n初始状态: {kf.get_state()}")
    
    # 生成模拟测量数据 (带噪声)
    measurements = []
    for i in range(100):
        # 真实位置
        true_pos = true_position + true_velocity * (i + 1) * 0.1
        # 添加测量噪声
        measurement = true_pos + np.random.normal(0, 0.05)
        measurements.append(measurement)
        true_position = true_pos
    
    # 进行滤波
    filtered_states = kf.filter(measurements)
    position, covariance = filtered_states
    
    print(f"最终位置估计: {position:.4f}")
    print(f"最终协方差: {covariance:.6f}")
    
    # 显示前几个测量和估计值
    print("\n前几个测量和滤波结果:")
    print("-" * 60)
    for i, m in enumerate(measurements[:5]):
        kf.update(m)
        print(f"测量 {i}: 测量={m:.4f}, 估计={kf.x_est[0,0]:.4f}, 协方差={kf.P[0,0]:.6f}")


def test_2d_kalman_filter():
    """测试多维卡尔曼滤波器 (带速度估计)"""
    print("\n" + "=" * 60)
    print("测试多维卡尔曼滤波 (带速度估计)")
    print("=" * 60)
    
    # 创建滤波器
    kf = KalmanFilterMultiDimension(dt=0.1)
    
    # 重置初始状态
    kf.reset(position=0.0, velocity=0.5)
    
    # 真实位置 (以 0.5 m/s 匀速运动)
    true_velocity = 0.5
    
    print(f"\n初始状态:")
    print(f"  位置: {kf.x_est[0, 0]:.4f}")
    print(f"  速度: {kf.x_est[1, 0]:.4f}")
    
    # 生成测量数据
    measurements = []
    for i in range(100):
        true_pos = true_velocity * (i + 1) * 0.1
        measurement = true_pos + np.random.normal(0, 0.03)
        measurements.append(measurement)
    
    # 进行滤波
    kf.filter(measurements)
    
    print(f"\n滤波后状态:")
    state = kf.get_state()
    print(f"  位置: {state['position']:.4f}")
    print(f"  速度: {state['velocity']:.4f}")
    print(f"  协方差: {state['covariance']:.6f}")


def example_usage():
    """使用示例"""
    print("\n" + "=" * 60)
    print("卡尔曼滤波使用示例")
    print("=" * 60)
    
    # 创建一个滤波器
    kf = KalmanFilter(dt=0.1)
    
    # 假设我们测量一个物体的位置，物体以约 0.3 m/s 的速度移动
    # 测量值为 0.2, 0.5, 0.8, 1.1, 1.4, ...
    
    measurements = [
        0.2, 0.5, 0.8, 1.1, 1.4,  # 理想情况
        0.3, 0.7, 1.2,  # 带噪声
        0.4, 0.6, 1.0, 1.5,  # 更多噪声
        0.35, 0.55, 1.2, 1.3, 1.6,  # 噪声变化
    ]
    
    print("\n测量序列:", measurements)
    print("\n滤波结果:")
    print("-" * 60)
    print(f"{'测量值':<10}{'估计值':<10}{'协方差':<10}")
    print("-" * 60)
    
    for i, measurement in enumerate(measurements):
        kf.update(measurement)
        state, cov = kf.get_state()
        print(f"{measurement:<10.2f} {state:<10.2f} {cov:<10.6f}")
    
    final_state, _ = kf.get_state()
    print(f"\n最终位置估计: {final_state:.2f}")


def visualize_kalman_filter():
    """
    可视化卡尔曼滤波效果
    
    注意: 这里需要安装 matplotlib
    """
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        print("\n" + "=" * 60)
        print("可视化卡尔曼滤波 (需要 matplotlib)")
        print("=" * 60)
        
        # 创建滤波器
        kf = KalmanFilter(dt=0.1)
        
        # 生成真实位置和带噪声测量
        true_positions = []
        measurements = []
        true_velocity = 0.5
        
        for i in range(200):
            true_pos = true_velocity * (i + 1) * 0.1
            true_positions.append(true_pos)
            measurement = true_pos + np.random.normal(0, 0.05)
            measurements.append(measurement)
            kf.update(measurement)
            estimated = float(kf.x_est[0, 0])
            
        # 绘图
        plt.figure(figsize=(10, 6))
        
        # 绘制真实位置
        plt.plot(range(len(true_positions)), true_positions, 'b-', 
                 label='真实位置', linewidth=2)
        
        # 绘制测量值
        plt.plot(range(len(measurements)), measurements, 'r.', 
                 label='测量值', markersize=8)
        
        # 绘制估计值
        plt.plot(range(len(true_positions)), estimated, 'g-', 
                 label='卡尔曼滤波估计', linewidth=2)
        
        # 添加图例和标题
        plt.xlabel('样本索引')
        plt.ylabel('位置 (米)')
        plt.title('卡尔曼滤波可视化')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        plt.show()
        
    except ImportError:
        print("matplotlib 未安装，请运行: pip install matplotlib")


if __name__ == "__main__":
    # 运行测试
    test_1d_kalman_filter()
    test_2d_kalman_filter()
    example_usage()
    visualize_kalman_filter()
    
    print("\n" + "=" * 60)
    print("卡尔曼滤波程序使用完成!")
    print("=" * 60)
