The logic is as following pseudo-code:

```python
if (product id in deny.txt):
    CANNOT use adb
else if (source ip == 10.206.25.235/23):
    CAN use adb
else:
    if (product id in allow.txt):
        CAN use adb
    else:
        CANNOT use adb
```