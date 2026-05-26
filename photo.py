import numpy as np

class MultiSensorInformationFilter:
    def __init__(self, dt=0.1):
        self.dt = dt
        # 状态维度: [x, vx, ax, y, vy, ay]^T
        self.dim = 6
        self.x = np.zeros((self.dim, 1))
        self.P = np.eye(self.dim) * 100
        
        # 状态转移矩阵 F (CA 模型)
        self.F = np.eye(self.dim)
        self.F[0, 1] = self.F[3, 4] = dt
        self.F[0, 2] = self.F[3, 5] = 0.5 * dt**2
        self.F[1, 2] = self.F[4, 5] = dt
        
    def step(self, z_radar, z_tdoa, gamma):
        # 1. 时间预测 (Predict)
        x_prior = self.F @ self.x
        P_prior = self.F @ self.P @ self.F.T + np.eye(self.dim) * 0.1
        
        # 转换为信息域
        Y_prior = np.linalg.inv(P_prior)
        y_prior = Y_prior @ x_prior
        
        # 2. 解析雅可比 (简化示例，实际需根据非线性模型计算 H)
        H_pass = np.eye(2, self.dim) # 假设观测位置
        H_tdoa = np.eye(2, self.dim)
        
        # 3. 前端 GMCC 抗差 (针对 RADAR)
        # 计算残差并重构 R
        res_radar = z_radar - H_pass @ x_prior
        E_k = res_radar.T @ res_radar
        sigma_k = 1.0 / (1.0 + E_k) # 自适应带宽
        W_k = np.exp(-E_k / (2 * sigma_k**2)) # 鲁棒权重
        R_tilde_pass = np.eye(2) / W_k
        
        # 4. 构建信息增量
        # RADAR:
        Y_pass = H_pass.T @ np.linalg.inv(R_tilde_pass) @ H_pass
        y_pass = H_pass.T @ np.linalg.inv(R_tilde_pass) @ z_radar
        
        # TDOA:
        R_tdoa = np.eye(2) * 5.0
        Y_tdoa = H_tdoa.T @ np.linalg.inv(R_tdoa) @ H_tdoa
        y_tdoa = H_tdoa.T @ np.linalg.inv(R_tdoa) @ z_tdoa
        
        # 5. 后端加性融合
        Y_post = Y_prior + Y_pass + (gamma * Y_tdoa)
        y_post = y_prior + y_pass + (gamma * y_tdoa)
        
        # 6. 逆映射恢复
        self.P = np.linalg.inv(Y_post)
        self.x = self.P @ y_post
        
        return self.x, self.P

# --- 模拟运行 ---
filter = MultiSensorInformationFilter()
# 模拟：RADAR观测, TDOA观测, 通信状态 gamma=1(正常)
z_radar = np.array([[10], [10]])
z_tdoa = np.array([[10.5], [9.5]])
est_x, est_P = filter.step(z_radar, z_tdoa, gamma=1)

print("当前时刻最优估计状态:\n", est_x.flatten())