### ADB logcat to Pandas DataFrame

```python
pip install a-pandas-ex-logcat2df

from a_pandas_ex_logcat2df import pd_add_adb_logcat_to_df
import pandas as pd
pd_add_adb_logcat_to_df()

adb_path = "C:\\Users\\USERNAME\\AppData\\Local\\Android\\Sdk\\platform-tools\\adb.exe"
deviceserial = "localhost:5745"
df = pd.Q_logcat2df(adb_path=adb_path, deviceserial=deviceserial,exit_keys='ctrl+x', timeout=None)


....
b'12-01 10:05:39.212 24637 24637 E System  : \tat android.app.Instrumentation.callApplicationOnCreate(Instrumentation.java:1053)\r\n'
b'12-01 10:05:39.212 24637 24637 E System  : \tat android.app.ActivityThread.handleBindApplication(ActivityThread.java:5418)\r\n'
b'12-01 10:05:39.212 24637 24637 E System  : \tat android.app.ActivityThread.-wrap2(ActivityThread.java)\r\n'
b'12-01 10:05:39.212 24637 24637 E System  : \tat android.app.ActivityThread$H.handleMessage(ActivityThread.java:1548)\r\n'
b'12-01 10:05:39.212 24637 24637 E System  : \tat android.os.Handler.dispatchMessage(Handler.java:102)\r\n'
b'12-01 10:05:39.212 24637 24637 E System  : \tat android.os.Looper.loop(Looper.java:154)\r\n'
b'12-01 10:05:39.212 24637 24637 E System  : \tat android.app.ActivityThread.main(ActivityThread.ja
....


# ctrl+x

Killing the process
df
Out[3]: 
                        aa_log_1  ...                                       aa_whole_log
0               audio_hw_primary  ...            audio_hw_primary: choose pcmC0D0p for 0
1      InputMethodManagerService  ...  InputMethodManagerService: packageName=com.goo...
2      InputMethodManagerService  ...  InputMethodManagerService: ime_enabled = false...
3      InputMethodManagerService  ...  InputMethodManagerService: packageName=com.goo...
4      InputMethodManagerService  ...  InputMethodManagerService: ime_enabled = false...
..                           ...  ...                                                ...
345               BitmapDrawable  ...       BitmapDrawable: BitmapDrawable cannot decode
346    android.widget.GridLayout  ...  android.widget.GridLayout: horizontal constrai...
347                         View  ...  View    : requestLayout() improperly called by...
348  WatchWhileTimeBarController  ...  WatchWhileTimeBarController: isScrubbing: no a...
349  WatchWhileTimeBarController  ...  WatchWhileTimeBarController: getDisplayCurrent...
[350 rows x 9 columns]

```

