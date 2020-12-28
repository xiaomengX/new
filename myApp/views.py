from django.shortcuts import render,redirect
from django.http import HttpResponse
from myApp.models import User
from myApp.forms import LoginForm,RegisterForm,ForgotForm
from scipy.io import wavfile
from sklearn.mixture import GaussianMixture
from .features import extract_features
from .gammatone import cochleagram_fft_coefs,spectrum_extractor,walet_gmm
from .email_send import send_email
import _pickle as cPickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
import librosa
import wave
import pyaudio
import datetime
import os
import time
import sys
# Create your views here.
def index(request):
    if request.method=='POST':
        return redirect("/base/")
#开始页面
def start(request):
    """Start page with a documentation.
    """
    return render(
        request,
        "django_sb_admin/login.html",
        {
            "nav_active": "start"
        }
    )
#登录
def login(request):
    """Start page with a documentation.
    """
    if request.session.get('is_login',None):
        return redirect('/base/')
    if request.method =="POST":
        login_form=LoginForm(request.POST)
        # message="请检查填写的内容！"
        if login_form.is_valid():
            username=login_form.cleaned_data.get('username')
            password=login_form.cleaned_data.get('password')
            try:
                user=User.objects.get(username=username)
            except:
                message="用户不存在!您是否已注册？？"
                return render(request,'django_sb_admin/login.html',locals())
            if user.password == password:
                request.session['is_login']=True
                request.session['user_id']=user.id
                request.session['user_name']=user.username
                return redirect('/base/')
            else:
                message="密码不正确！"
                return render(request,'django_sb_admin/login.html',locals())
        else:
            return render(request,'django_sb_admin/login.html',locals())
    else:
        login_form = LoginForm()
    return render(request,'django_sb_admin/login.html',{'login_form': login_form})
#注销
def logout(request):
    if not request.session.get('is_login',None):
        return redirect("/login/")
    request.session.flush()
    return redirect("/login/")
#注册
def register(request):
    if request.session.get('is_login',None):
        return redirect('/base/')
    if request.method=='POST':
        register_form=RegisterForm(request.POST)
        message="请检查填写的内容！"
        if register_form.is_valid():
            username=register_form.cleaned_data.get('username')
            password=register_form.cleaned_data.get('password')
            confirmPassword=register_form.cleaned_data.get('confirmPassword')
            email=register_form.cleaned_data.get('email')
            sex=register_form.cleaned_data.get('sex')
            if password!=confirmPassword:
                message='两次输入的密码不同！'
                return render(request,'django_sb_admin/register.html',locals())
            else:
                same_user_name=User.objects.filter(username=username)
                if same_user_name:
                    message='用户名已存在！'
                    return  render(request,'django_sb_admin/register.html',locals())
                same_user_email=User.objects.filter(email=email)
                if same_user_email:
                    message='该邮箱已被注册了！'
                    return render(request,'django_sb_admin/register.html',locals())
                new_user = User()
                new_user.username = username
                new_user.password = password
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                return redirect('/login/')
        else:
            return render(request,'django_sb_admin/register.html',locals())
    else:
        register_form = RegisterForm()
    return render(request,'django_sb_admin/register.html',{'register_form':register_form})

#忘记密码
def forgot(request):
    if request.method == "POST":
        forgot_form = ForgotForm(request.POST)
        # message="请检查填写的内容！"
        if forgot_form.is_valid():
            email = forgot_form.cleaned_data.get('email')
            try:
                user = User.objects.get(email=email)
            except:
                message = "用户注册的邮箱不存在!您是否已注册？？"
                return render(request, 'django_sb_admin/forgot_password.html', locals())
            send_email(user.email,user.password)
            return redirect('/login/')
        else:
            return render(request, 'django_sb_admin/forgot_password.html', locals())
    else:
        forgot_form = ForgotForm()
    return render(request, 'django_sb_admin/forgot_password.html', {'forgot_form': forgot_form})

#主页面
def base(request):
    """Dashboard page.
    """
    if not request.session.get('is_login',None):
        return redirect('/login/')
    return render(
        request,
        "django_sb_admin/base.html",
    )

#录制声纹
CHUNK=1024
FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
RECORD_SECONDS=3
def record(request):
    p=pyaudio.PyAudio()
    stream=p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)
    print("* recording")
    # record_message ="* 开始录制语音，只有三秒钟，请抓紧时间！"
    frames=[]
    for i in range(0,int(RATE / CHUNK * RECORD_SECONDS)):
        data=stream.read(CHUNK)
        frames.append(data)
        record_message=" * 录制完成，如果次数少于五次，建议您继续录制 *"
    stream.stop_stream()
    stream.close()
    p.terminate()
    filename="speech//"+request.session['user_name']
    if not os.path.exists(filename):
        os.mkdir(filename)
    wf = wave.open(filename + "//" + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H-%M-%S') + '.wav',
                   'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return render(
        request,
        "django_sb_admin/sb_admin_dashboard.html",{"record_message":record_message}
    )
#播放语音文件
def play(request):
    filename="speech/"+request.session['user_name']
    fileList=os.listdir(filename)
    Image=[]
    count=0
    for i in fileList[-3:]:
        count+=1
        wf = wave.open(filename+"/"+i, 'rb')
        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        data = wf.readframes(CHUNK)
        while data != b'':
            stream.write(data)
            data = wf.readframes(CHUNK)
        stream.stop_stream()
        stream.close()
        p.terminate()
        sr,wave1=wavfile.read(filename+"/"+i)
        sample_number=wave1.shape[0]
        total_time=int(sample_number /sr *1000)
        time_series=np.linspace(0,total_time,sample_number)
        fig,ax=plt.subplots(1,1)
        ax.plot(time_series,wave1)
        ax.set_title('Time*Amplitude')
        ax.set_xlabel('Time/ms')
        ax.set_ylabel('Amplitude/dB')
        Imagename="myApp/static/Image/"
        if not os.path.exists(Imagename):
            os.mkdir(Imagename)
        plt.savefig(Imagename+'/'+'play'+str(count)+'.png')
    message="ok"
    return render(
        request,
        "django_sb_admin/sb_admin_dashboard.html",
        locals()
    )

def dashboard(request):
    """Dashboard page.
    """
    return render(
        request,
        "django_sb_admin/sb_admin_dashboard.html",
        {
            "nav_active": "dashboard"
        }
    )
def progress_bar():
    for i in range(1, 101):
        print("\r", end="")
        print("Download progress: {}%: ".format(i), "▋" * (i // 2), end="")
        sys.stdout.flush()
        time.sleep(0.5)
#训练声纹
def training(request):
    feature=np.asarray(())
    filename="speech/"+request.session['user_name']
    for root,dirs,files in os.walk(filename):
        print(files)
        for i in files:
            sr,audio=wavfile.read(filename+'/'+i)
            vector=extract_features(audio,sr)
            if feature.size==0:
                feature=vector
            else:
                feature=np.vstack((feature,vector))
        gmm=GaussianMixture(n_components=16,covariance_type='diag')
        gmm.fit(feature)
        picklefile=request.session['user_name']+".gmm"
        cPickle.dump(gmm,open("myApp//static//speaker//"+picklefile,"wb"))
        progress_bar()
        print('+ modeling completed for speaker:',picklefile," with data point = ",feature.shape)
        message="，您的训练完成，可以开始身份认证啦！"
    return render(request, "django_sb_admin/sb_admin_charts.html",
                  {"nav_active":"charts","message":message})

#语音认证测试
def speech_record(request):
    p=pyaudio.PyAudio()
    stream=p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)
    print("* recording")
    frames=[]
    for i in range(0,int(RATE / CHUNK * RECORD_SECONDS)):
        data=stream.read(CHUNK)
        frames.append(data)
    speech_recordmessage=" * 录制完成，开始您的认证吧！"
    stream.stop_stream()
    stream.close()
    p.terminate()
    filename="speech_test/"+request.session['user_name']
    if not os.path.exists(filename):
        os.mkdir(filename)
    wf = wave.open(filename + "/" + 'test.wav',
                   'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    return render(
        request,
        "django_sb_admin/sb_admin_tables.html",
        locals()
    )
def testing(request):
    model_path="myApp/static/speaker/"
    gmm_files=[os.path.join(model_path,fname) for fname in os.listdir(model_path)
               if fname.endswith('.gmm')]
    models=[cPickle.load(open(fname,'rb')) for fname in gmm_files]
    speakers=[fname.split('/')[-1].split(".gmm")[0] for fname in gmm_files]
    # print(speakers)
    filename = "speech_test/" + request.session['user_name']
    for root,dirs,files in os.walk(filename):
        for i in files:
            sr, audio = wavfile.read(filename + '/' + i)
            vector=extract_features(audio,sr)
            log_likelihood=np.zeros(len(models))
            for j in range(len(models)):
                gmm=models[j]
                scores=np.array(gmm.score(vector))
                log_likelihood[j]=scores.sum()
            winner=np.argmax(log_likelihood)
            print("/////",winner)
            if speakers[winner]==request.session['user_name']:
                message1=",您好！欢迎您使用本系统！！"
                # print("hello")
            else:
                message2=",这个声音不是您的,请本人来认证！！！"
    return render(request, "django_sb_admin/sb_admin_tables.html",
                  locals())
#预加重
def pre_emphasis(request):
    filename = "speech/" + request.session['user_name']
    fileList = os.listdir(filename)
    Image = []
    count = 0
    for i in fileList[-3:]:
        count+=1
        sample_rate,signal=wavfile.read(filename+"/"+i)
        pre_em=0.97
        emphasized_signal=np.append(signal[0],signal[1:]-pre_em * signal[:-1])
        plt.plot(emphasized_signal)
        Imagename = "myApp/static/Image/"
        if not os.path.exists(Imagename):
            os.mkdir(Imagename)
        plt.savefig(Imagename + '/' + 'pre_emphasis' + str(count) + '.png')
        # print("ok")
    pre_message="ok"
    return render(request, "django_sb_admin/sb_admin_blank.html",
                      {"nav_active": "blank","pre_message":pre_message})

#分帧
def Framing(request):
    filename = "speech/" + request.session['user_name']
    fileList = os.listdir(filename)
    Image = []
    count = 0
    for i in fileList[-3:]:
        count += 1
        sample_rate, signal = wavfile.read(filename + "/" + i)
        pre_em = 0.97
        emphasized_signal = np.append(signal[0], signal[1:] - pre_em * signal[:-1])
        frame_size = 0.025
        frame_stride = 0.1
        frame_length, frame_step = frame_size * sample_rate, frame_stride * sample_rate
        signal_length = len(emphasized_signal)
        frame_length = int(round(frame_length))
        frame_step = int(round(frame_step))
        num_frames = int(np.ceil(float(np.abs(signal_length - frame_length)) / frame_step))
        pad_signal_length = num_frames * frame_step + frame_length
        z = np.zeros((pad_signal_length - signal_length))
        pad_signal = np.append(emphasized_signal, z)
        indices = np.tile(np.arange(0, frame_length), (num_frames, 1)) + np.tile(
        np.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T
        frames = pad_signal[np.mat(indices).astype(np.int32, copy=False)]
        plt.plot(frames)
        Imagename = "myApp/static/Image/"
        if not os.path.exists(Imagename):
            os.mkdir(Imagename)
        plt.savefig(Imagename + '/' + 'Framing' + str(count) + '.png')
        # print("ok")
    Frame_message = "ok"
    return render(request, "django_sb_admin/sb_admin_Framing.html",
                  {"nav_active": "blank", "Frame_message": Frame_message})
#加窗
def hamm(request):
    filename = "speech/" + request.session['user_name']
    fileList = os.listdir(filename)
    Image = []
    count = 0
    for i in fileList[-3:]:
        count += 1
        sample_rate, signal = wavfile.read(filename + "/" + i)
        pre_em = 0.97
        emphasized_signal = np.append(signal[0], signal[1:] - pre_em * signal[:-1])
        frame_size = 0.025
        frame_stride = 0.1
        frame_length, frame_step = frame_size * sample_rate, frame_stride * sample_rate
        signal_length = len(emphasized_signal)
        frame_length = int(round(frame_length))
        frame_step = int(round(frame_step))
        num_frames = int(np.ceil(float(np.abs(signal_length - frame_length)) / frame_step))
        pad_signal_length = num_frames * frame_step + frame_length
        z = np.zeros((pad_signal_length - signal_length))
        pad_signal = np.append(emphasized_signal, z)
        indices = np.tile(np.arange(0, frame_length), (num_frames, 1)) + np.tile(
            np.arange(0, num_frames * frame_step, frame_step), (frame_length, 1)).T
        frames = pad_signal[np.mat(indices).astype(np.int32, copy=False)]
        frames *= np.hamming(frame_length)
        plt.plot(frames)
        Imagename = "myApp/static/Image/"
        if not os.path.exists(Imagename):
            os.mkdir(Imagename)
        plt.savefig(Imagename + '/' + 'hamm' + str(count) + '.png')
        # print("ok")
    hamm_message = "ok"
    return render(request, "django_sb_admin/sb_admin_hamm.html",
                  {"nav_active": "blank", "hamm_message": hamm_message})
#MFCC
def mfcc(request):
    filename = "speech/" + request.session['user_name']
    fileList = os.listdir(filename)
    Image = []
    count = 0
    for i in fileList[-3:]:
        count += 1
        sample_rate, signal = wavfile.read(filename + "/" + i)
        combined=extract_features(signal,sample_rate)
        plt.plot(combined)
        Imagename = "myApp/static/Image/"
        if not os.path.exists(Imagename):
            os.mkdir(Imagename)
        plt.savefig(Imagename + '/' + 'mfcc' + str(count) + '.png')
        # print("ok")
    mfcc_message = "ok"
    return render(request, "django_sb_admin/sb_admin_mfcc.html",
                  {"nav_active": "blank", "mfcc_message": mfcc_message})
#Gammatone滤波器
def gammatone(request):
    filename = "speech/" + request.session['user_name']
    fileList = os.listdir(filename)
    Image = []
    count = 0
    for i in fileList[-3:]:
        count += 1
        sample_rate, signal = wavfile.read(filename + "/" + i)
        combined = walet_gmm(signal,sample_rate)
        fft2gammatone_coef=cochleagram_fft_coefs(sample_rate,320,64)
        spect=spectrum_extractor(combined,320,160,'hamming',False)
        gammatone_speech=np.flipud(np.sqrt(np.matmul(fft2gammatone_coef,spect)))
        plt.plot(gammatone_speech)
        Imagename = "myApp/static/Image/"
        if not os.path.exists(Imagename):
            os.mkdir(Imagename)
        plt.savefig(Imagename + '/' + 'gammatone' + str(count) + '.png')
        # print("ok")
    gammatone_message = "ok"
    return render(request, "django_sb_admin/sb_admin_GTG.html",
                  {"nav_active": "blank", "gammatone_message": gammatone_message})

#话筒登录模式
def huatong_speech(request):
    count=0
    if count<3:
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        print("* recording")
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        speech_recordmessage = " * 录制完成，开始您的认证吧！"
        stream.stop_stream()
        stream.close()
        p.terminate()
        filename = "testing"
        if not os.path.exists(filename):
            os.mkdir(filename)
        wf = wave.open(filename + "/" + 'test.wav',
                       'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        model_path = "myApp/static/speaker/"
        gmm_files = [os.path.join(model_path, fname) for fname in os.listdir(model_path)
                     if fname.endswith('.gmm')]
        models = [cPickle.load(open(fname, 'rb')) for fname in gmm_files]
        speakers = [fname.split('/')[-1].split(".gmm")[0] for fname in gmm_files]
        print(speakers)
        filename = "testing/"
        for root, dirs, files in os.walk(filename):
            for i in files:
                sr, audio = wavfile.read(filename + '/' + i)
                vector = extract_features(audio, sr)
                log_likelihood = np.zeros(len(models))
                for j in range(len(models)):
                    gmm = models[j]
                    scores = np.array(gmm.score(vector))
                    log_likelihood[j] = scores.sum()
                winner = np.argmax(log_likelihood)
                print(winner)
                print("/////speakers[winner] ==", winner)
                print(User.objects.filter(username=speakers[winner]).first())
                if User.objects.filter(username=speakers[winner]).first():
                    # message1 = ",您好！欢迎您使用本系统！！"
                    request.session['is_login'] = True
                    # request.session['user_id'] =
                    request.session['user_name'] = speakers[winner]
                    print("hello")
                    print(request.session['user_name'] )
                    return redirect('/base/')
                else:
                    message2 = ",这个声音不是您的,请本人来认证！！！"
                    print("111111")
                    login_form = LoginForm()
                    return render(request, 'django_sb_admin/login.html', {'login_form': login_form})
                    # return render(request, 'django_sb_admin/login.html', locals())
        count+=1
    else:
        login_form = LoginForm()
        return render(request, 'django_sb_admin/login.html', {'login_form': login_form})


def myajaxtestview(request):
    return HttpResponse(request.POST['text'])

def charts(request):
    """Charts page.
    """
    return render(request, "django_sb_admin/sb_admin_charts.html",
                  {"nav_active":"charts"})
def tables(request):
    """Tables page.
    """
    return render(request, "django_sb_admin/sb_admin_tables.html",
                  {"nav_active":"tables"})
def forms(request):
    """Forms page.
    """
    return render(request, "django_sb_admin/sb_admin_forms.html",
                  {"nav_active":"forms"})
def bootstrap_elements(request):
    """Bootstrap elements page.
    """
    return render(request, "django_sb_admin/sb_admin_bootstrap_elements.html",
                  {"nav_active":"bootstrap_elements"})
def bootstrap_grid(request):
    """Bootstrap grid page.
    """
    return render(request, "django_sb_admin/sb_admin_bootstrap_grid.html",
                  {"nav_active":"bootstrap_grid"})
# def dropdown(request):
#     """Dropdown  page.
#     """
#     return render(request, "django_sb_admin/sb_admin_dropdown.html",
#                   {"nav_active":"dropdown"})
def rtl_dashboard(request):
    """RTL Dashboard page.
    """
    return render(request, "django_sb_admin/sb_admin_rtl_dashboard.html",
                  {"nav_active":"rtl_dashboard"})

def blank(request):
    """Blank page.
    """
    return render(request, "django_sb_admin/sb_admin_blank.html",
                  {"nav_active":"blank"})
def blank_framing(request):
    return render(request, "django_sb_admin/sb_admin_Framing.html",
                  {"nav_active": "blank"})
def blank_hamm(request):
    return render(request, "django_sb_admin/sb_admin_hamm.html",
                  {"nav_active": "blank"})
def blank_mfcc(request):
    return render(request, "django_sb_admin/sb_admin_mfcc.html",
                  {"nav_active": "blank"})
def blank_GTG(request):
    return render(request, "django_sb_admin/sb_admin_GTG.html",
                  {"nav_active": "blank"})


num_progress = 0 # 当前的后台进度值（不喜欢全局变量也可以很轻易地换成别的方法代替）

def process_data(request):
    # ...
    for i in range(12345):
        # ... 数据处理业务
        num_progress = i * 100 / 12345; # 更新后台进度值，因为想返回百分数所以乘100
    return JsonResponse(res, safe=False)

def show_progress(request):
    return JsonResponse(num_progress, safe=False)

