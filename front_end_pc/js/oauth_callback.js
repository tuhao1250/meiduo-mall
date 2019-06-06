var vm = new Vue({
    el: '#app',
    data: {
        host: host,
        is_show_waiting: true,

        error_password: false,
        error_mobile: false,
        error_sms_code: false,
        error_mobile_message: '',
        error_sms_code_message: '',
        error_image_code: false,
        error_image_code_message: '',


        sms_code_tip: '获取短信验证码',
        sending_flag: false, // 正在发送短信标志

        image_code_id: '', // 图片验证码id
        image_code_url: '',
        password: '',
        mobile: '',
        sms_code: '',
        access_token: '',
        image_code: '',

    },
    mounted: function(){
        // 从路径中获取qq重定向返回的code
        var code = this.get_query_string('code');
        axios.get(this.host + 'oauth/qq/user/?code=' + code, {
                responseType: 'json',
                withCredentials: true
            })
            .then(response => {
                if (response.data.user_id){
                    // 用户已绑定
                    sessionStorage.clear();
                    localStorage.clear();
                    localStorage.user_id = response.data.user_id;
                    localStorage.username = response.data.username;
                    localStorage.token = response.data.token;
                    var state = this.get_query_string('state');
                    location.href = state;
                } else {
                    // 用户未绑定
                    this.access_token = response.data.access_token;
                    this.is_show_waiting = false;
                    this.get_image_code()
                }
            })
            .catch(error => {
                console.log(error.response.data);
                alert('服务器异常');
            })
    },
    methods: {
        // 生成uuid
        generate_uuid: function(){
            var d = new Date().getTime();
            if(window.performance && typeof window.performance.now === "function"){
                d += performance.now(); //use high-precision timer if available
            }
            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                var r = (d + Math.random()*16)%16 | 0;
                d = Math.floor(d/16);
                return (c =='x' ? r : (r&0x3|0x8)).toString(16);
            });
            return uuid;
        },
        get_image_code: function(){
            this.image_code_id = this.generate_uuid();
            this.image_code_url = this.host + "image_codes/" + this.image_code_id + "/";
        },
        // 获取url路径参数
        get_query_string: function(name){
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return decodeURI(r[2]);
            }
            return null;
        },
        check_pwd: function (){
            var len = this.password.length;
            this.error_password = len < 8 || len > 20;
        },
        check_mobile: function () {
            var re = /^((13[0-9])|(14[5,7,9])|(15[0-3,5-9])|(18[0-9])|(17[0,1,3,5,6,7,8]))\d{8}$/;
            if (re.test(this.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile = true;
                this.error_mobile_message = "您输入的手机号码格式不正确";
            }
        },
        check_sms_code: function(){
            if(!this.sms_code){
                this.error_sms_code_message = '请填写短信验证码';
                this.error_sms_code = true;
            } else {
                this.error_sms_code = false;
            }
        },
        check_image_code: function () {
            if (!this.image_code) {
                this.error_image_code = true;
                this.error_image_code_message = "请填写图片验证码";
            } else {
                this.error_image_code = false;
            }
        },
        // 发送手机短信验证码
        send_sms_code: function () {  // 发送短信验证码
            // 如果当前已经发送过验证码,且在60s内,则不允许发送短息
            // console.log("点击了获取短信的接口")
            if (this.sending_flag) {
                return;
            }
            // 将发送短信标记为真
            this.sending_flag = true;
            // 1. 检验手机号和图片验证码是否填写,
            this.check_image_code();
            this.check_mobile();
            if (this.error_mobile || this.error_image_code) {
                this.sending_flag = false;  // 重置标记
                return;
            }
            // 2. 调用后端接口
            axios.get(this.host + "sms_codes/" + this.mobile +
                "/?image_code_id=" + this.image_code_id + "&text=" + this.image_code, {
                responseType: 'json'  // 要求后端返回数据格式json
            })
                .then(response => {
                    var num = 60;
                    var t = setInterval(() => {
                        if (num === 1) {
                            clearInterval(t);
                            this.sending_flag = false;
                            this.sms_code_tip = '获取短信验证码';
                        } else {
                            num -= 1;
                            this.sms_code_tip = num + '秒'
                        }
                    }, 1000)
                })
                .catch(error => {
                    if (error.response.status === 400) {
                        this.error_image_code_message = "图片验证码有误";
                        this.error_image_code = true;
                        this.get_image_code();  // 重新获取图片验证码
                    } else {
                        console.log(error.response.data)
                    }
                    this.sending_flag = false;
                })

        },
        // 保存
        on_submit: function(){
            this.check_pwd();
            this.check_mobile();
            this.check_sms_code();
            if(!this.error_password && !this.error_mobile && !this.error_sms_code){
                axios.post(this.host + "oauth/qq/user/", {
                    "sms_code": this.sms_code,
                    "mobile": this.mobile,
                    "password": this.password,
                    "access_token": this.access_token
                }, {
                    responseType: 'json',
                    withCredentials: true
                })
                    .then(response=>{
                        // 记住用户登录状态
                        sessionStorage.clear();
                        localStorage.clear();
                        localStorage.token = response.data.token;
                        localStorage.user_id = response.data.id;
                        localStorage.username = response.data.username;
                        location.href = this.get_query_string('state');
                    })
                    .catch(error=>{
                        if (error.response.status === 400) {
                            this.error_sms_code_message = error.response.data.message;
                            this.error_sms_code = true;
                        } else {
                            console.log(error.response.data);
                        }
                    })
            }

        }
    }
});