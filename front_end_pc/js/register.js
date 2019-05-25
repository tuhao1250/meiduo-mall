var vm = new Vue({
    el: '#app',
    data: {
        host,
        error_name: false,
        error_password: false,
        error_check_password: false,
        error_mobile: false,
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
        err_username_message: '请输入5-20个字符的用户名',  // 用户名错误信息
        err_mobile_message: '您输入的手机号码格式不正确',  // 手机号码错误信息
    },
    mounted: function () {
        this.get_image_code();
    },
    methods: {
        get_image_code: function () {  // 刷新图片验证码
            this.image_code_id = this.generate_uuid();
            this.image_code_url = this.host + "image_codes/" + this.image_code_id + "/";
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
                            this.sms_code_tip = "短息已发送,请在 " + num + ' 秒后重新获取'
                        }
                    }, 1000)
                })
                .catch(error => {
                    if (error.response.status === 400) {
                        this.err_image_code_message = "图片验证码有误";
                        this.error_image_code = true;
                        this.get_image_code();  // 重新获取图片验证码
                    } else {
                        console.log(error.response.data)
                    }
                    this.sending_flag = false;
                })

        },
        check_username: function () {
            var len = this.username.length;
            if (len < 5 || len > 20) {
                this.err_username_message = '请输入5-20个字符的用户名';
                this.error_name = true;
            } else {
                this.error_name = false;
            }
            if (!this.error_name) {
                axios.get(this.host + "usernames/" + this.username + "/count/", {
                    responseType: 'json'
                })
                    .then(response => {
                        if (response.data.count > 0) {
                            this.err_username_message = "用户名已存在!";
                            this.error_name = true;
                        } else {
                            this.error_name = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response.data);
                    })
            }
        },
        check_pwd: function () {
            var len = this.password.length;
            this.error_password = len < 8 || len > 20;
        },
        check_cpwd: function () {
            this.error_check_password = !(this.password === this.password2);
        },
        check_mobile: function () {
            var re = /^((13[0-9])|(14[5,7,9])|(15[0-3,5-9])|(18[0-9])|(17[0,1,3,5,6,7,8]))\d{8}$/;
            if (re.test(this.mobile)) {
                this.error_mobile = false;
            } else {
                this.error_mobile = true;
                this.err_mobile_message = "您输入的手机号码格式不正确";
            }
            if (!this.error_mobile) {
                axios.get(host + "mobiles/" + this.mobile + "/count/", {
                    responseType: "json"
                })
                    .then(response => {
                        if (response.data.count > 0) {
                            this.err_mobile_message = '手机号已存在';
                            this.error_mobile = true;
                        } else {
                            this.error_mobile = false;
                        }
                    })
                    .catch(error => {
                        console.log(error.response.data);
                    })
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
            this.error_allow = !this.allow;
        },
        // 注册
        on_submit: function () {
            this.check_username();
            this.check_pwd();
            this.check_cpwd();
            this.check_mobile();
            this.check_image_code();
            this.check_sms_code();
            this.check_allow();

            if (!this.error_name && !this.error_password && !this.error_check_password && !this.error_mobile
                && !this.error_allow && !this.error_sms_code) {
                axios.post(this.host + 'users/', {
                    username: this.username,
                    password: this.password,
                    password2: this.password2,
                    mobile: this.mobile,
                    sms_code: this.sms_code,
                    allow: this.allow.toString()
                }, {
                    responseType: 'json'
                })
                    .then(response => {
                        localStorage.clear();
                        sessionStorage.clear();
                        localStorage.token = response.data.token;  // 本地存储认证token
                        localStorage.username = response.data.username;  // 存储用户名
                        localStorage.user_id = response.data.id;  // 存储用户id
                        location.href = '/index.html';  // 重定向到首页
                    })
                    .catch(error => {
                        // 发生错误后,图形验证码需要刷新,清除图片验证码以及短信验证码字段的内容,
                        this.image_code = "";
                        this.sms_code = "";
                        this.get_image_code();
                        if (error.response.status === 400) {
                            if ('non_field_errors' in error.response.data) {
                                this.err_sms_code_message = error.response.data.non_field_errors[0];
                            } else {
                                this.err_sms_code_message = '数据有误';
                            }
                            this.error_sms_code = true;
                        } else {
                            console.log(error.response.data);
                        }
                    })
            }
        }
    }
});
