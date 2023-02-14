公式计算器 
============  
**提供期货相关的日期、代码、数据获取等工具（目前只支持股指期货（IC、IF、IH））**  

1. basis_utils                               
    - get_price                           _获取价格数据，支持高频_ 
    - get_basis                           _获取基差_  
    - get_days_to_prompt                  _获取距离交割日的天数_ 
    - get_basis_div_days_to_prompt        _获取平均基差_ 
2. code_utils                           
    - get_futures_code_by_date            _根据日期获取主力期货的代码_  
    - get_next_futures_code               _获取下一期主力合约的代码_  
    - get_last_futures_code               _获取上一期主力合约的代码_  
3. date_utils                         
    - get_prompt_date                     _根据年月获取交割日_  
    - get_prompt_date_by_futures_code     _根据期货代码获取交割日_  
    - get_next_month                      _获取下个月日期_  
    - get_last_month                      _获取上个月日期_  
    - get_range_date_by_futures_code      _根据期货代码，获取日期序列_ 
    - get_days_to_prompt_by_futures_code  _根据期货代码和日期获取到期天数_
