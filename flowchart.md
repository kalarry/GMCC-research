graph TD
    %% 样式定义
    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px;
    classDef input_output fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef process fill:#fff3e0,stroke:#f57c00,stroke-width:2px;
    classDef split_process fill:#f1f8e9,stroke:#689f38,stroke-width:2px;

    subgraph InputZone ["【k 时刻输入】"]
        I["• 上一时刻后验状态: X̂_{k-1|k-1} , P_{k-1|k-1}<br>• 当前量测: Z_k = { z_{k,pass} , z_{k,tdoa} }<br>• 通信状态: γ_k = { γ_{k,pass}=1 , γ_{k,tdoa} ∈ {0,1} }"]
    end

    S1["【1. 时间预测步】<br>CA 模型 (F, Q)<br>X̂_{k|k-1} = F X̂_{k-1|k-1}<br>P_{k|k-1} = F P_{k-1|k-1}F' + Q"]
    S2["【2. 解析线性化】<br>闭式雅可比矩阵<br>H_{k,pass} , H_{k,tdoa}"]

    S3a["【3. 前端 GMCC 抗差 (pass)】<br>仅当 γ_{k,pass}=1 时：<br>• 新息残差 ε_k<br>• 马氏能量 E_k<br>• 自适应核带宽 σ_k<br>• 鲁棒权重 W_k<br>• R̃_{k,pass} = R_pass / W_k"]
    S3b["【TDOA 通道预处理】<br>• 标称协方差 R_tdoa<br>• 伯努利因子 γ_{k,tdoa}<br>(保留至后端)"]

    S4["【4. 信息域投影】<br>Y_{k|k-1} = P_{k|k-1}^{-1}<br>y_{k|k-1} = Y_{k|k-1} X̂_{k|k-1}"]
    S5["【5. 信息增量构筑】<br>ΔY_{k,pass} = H' R̃^{-1} H<br>Δy_{k,pass} = H' R̃^{-1}(ε+HX̂)<br>(TDOA 同理，使用 R_tdoa)"]
    S6["【6. 后端加性融合】<br>Y_{k|k} = Y_{k|k-1} + ΔY_pass + γ_{k,tdoa}·ΔY_tdoa<br>y_{k|k} = y_{k|k-1} + Δy_pass + γ_{k,tdoa}·Δy_tdoa"]
    S7["【7. 状态反演】<br>P_{k|k} = Y_{k|k}^{-1}<br>X̂_{k|k} = P_{k|k}·y_{k|k}"]

    Output["【输出】<br>全局后验 X̂_{k|k}, P_{k|k}"]

    %% 流程连线
    I --> S1
    S1 --> S2
    
    %% 并行处理分支
    S2 --> S3a
    S2 --> S3b
    S3a --> S4
    S3b --> S4
    
    S4 --> S5
    S5 --> S6
    S6 --> S7
    S7 --> Output

    %% 反馈回路 (使用虚线表示)
    Output -. "反馈至下一时刻 k+1" .-> I

    %% 应用样式
    class I,Output input_output;
    class S1,S2,S4,S5,S6,S7 process;
    class S3a,S3b split_process;
