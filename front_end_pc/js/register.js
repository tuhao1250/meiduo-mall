var vm = new Vue({
    el: '#app',
    data: {
        error_name: false,
        error_password: false,
        error_check_password: false,
        error_phone: false,
        error_allow: false,
        error_image_code: false,
        error_sms_code: false,

        username: '',
        password: '',
        password2: '',
        mobile: '',
        sms_code: '',
        allow: false,
        image_code: '',
        image_code_id: '',
        image_code_url: '',
        sms_code_tip: '获取短信验证码',
        sending_flag: false,  // 是否发送过短信验证码
        err_image_code_message: '请填写图片验证码',  // 图片验证码错误信息
        err_sms_code_message: '请填写短信验证码',  // 短信验证码错误信息
    },
    mounted: function () {
        this.get_image_code();
    },
    methods: {
        get_image_code: function () {  // 刷新图片验证码
            this.image_code_id = this.generate_uuid();
            this.image_code_url = "http://127.0.0.1:8000/image_codes/" + this.image_code_id + "/";
        },
        generate_uuid: function () {
            var d = new Date().getTime();
            if (window.performance && typeof window.performance.now == "function") {
                d += performance.now();  // use high-precision timer if available
            }
            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                var r = (d + Math.random() * 16) % 16 | 0;
                d = Math.floor(d / 16);
                return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
            return uuid;
        },
        send_sms_code: function () {  // 发送短信验证码
            // 如果当前已经发送过验证码,且在60s内,则不允许发送短息
            console.log("点击了获取短信的接口")
            if (this.sending_flag) {
                return;
            }
            // 将发送短信标记为真
            this.sending_flag = true;
            // 1. 检验手机号和图片验证码是否填写,
            this.check_image_code();
            this.check_phone();
            if (this.error_phone || this.error_image_code) {
                this.sending_flag = false;  // 重置标记
                return;
            }
            // 2. 调用后端接口
            axios.get(host + "sms_codes/" + this.mobile +
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
                    if(error.response.status === 400){
                        this.err_image_code_message = "图片验证码有误";
                        this.error_image_code = true;
                    }
                    else{
                        console.log(error.response.data)
                    }
                    this.sending_flag = false;
                })

        },
        check_username: function () {
            var len = this.username.length;
            if (len < 5 || len > 20) {
                this.error_name = true;
            } else {
                this.error_name = false;
            }
        },
        check_pwd: function () {
            var len = this.password.length;
            if (len < 8 || len > 20) {
                this.error_password = true;
            } else {
                this.error_password = false;
            }
        },
        check_cpwd: function () {
            if (this.password != this.password2) {
                this.error_check_password = true;
            } else {
                this.error_check_password = false;
            }
        },
        check_phone: function () {
            var re = /^((13[0-9])|(14[5,7,9])|(15[0-3,5-9])|(18[0-9])|(17[0,1,3,5,6,7,8]))\d{8}$/;
            if (re.test(this.mobile)) {
                this.error_phone = false;
            } else {
                this.error_phone = true;
            }
        },
        check_image_code: function () {
            if (!this.image_code) {
                this.error_image_code = true;
                this.err_image_code_message = "请填写图片验证码";
            } else {
                this.error_image_code = false;
            }
        },
        check_sms_code: function () {
            if (!this.sms_code) {
                this.error_sms_code = true;
                this.err_sms_code_message = "请填写短信验证码";

            } else {
                this.error_sms_code = false;
            }
        },
        check_allow: function () {
            if (!this.allow) {
                this.error_allow = true;
            } else {
                this.error_allow = false;
            }
        },
        // 注册
        on_submit: function () {
            this.check_username();
            this.check_pwd();
            this.check_cpwd();
            this.check_phone();
            this.check_image_code();
            this.check_sms_code();
            this.check_allow();
        }
    }
});
