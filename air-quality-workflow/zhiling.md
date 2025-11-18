## Azure SQL 连接测试指南（Device Code 模式）

1. **安装依赖（若尚未安装）**
   ```powershell
   pip install azure-identity
   ```

2. **执行连接测试脚本**
   ```powershell
   python device_connect_test.py
   ```

3. **根据提示完成登录**
   - 终端会输出“ open https://microsoft.com/devicelogin and enter the code ABCD1234 ”这类提示；
   - 用浏览器访问该链接，输入代码，使用 `sc22wn@leeds.ac.uk` 完成密码/MFA 验证；
   - 验证成功后回到终端即可看到 `Sample row: ...` 和 `Connected OK`。
