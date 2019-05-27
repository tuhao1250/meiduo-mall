var vm = new Vue({
    el: '#app',
    data: {
        host,
        is_show_form_1: true,  // 是否显示表单1
        is_show_form_2: false,
        is_show_form_3: false,
        is_show_form_4: false,

        mobile: '',  // 后端返回的手机号
        username: '',
        user_id: '',
        image_code: '',
        image_code_id: '',
        image_code_url: '',
        sms_code: '',
        password: '',
        password2: '',
        access_token: '',

        error_username: false,
        error_image_code: false,
        error_sms_code: false,
        error_password: false,
        error_check_password: false,
        sending_flag: false,  // 发送短信的标志

        error_image_code_message: '请填写验证码',
        error_username_message: '请填写用户名或手机号',
        error_sms_code_message: '请填写短信验证码',
        error_pwd_message: '仅允许8~20个字符的密码',
        error_check_pwd_message: '两次输入的密码不一致',
        sms_code_tip: '获取短信验证码',

        // 控制进度条显示
        step_class: {
            'step-1': true,
            'step-2': false,
            'step-3': false,
            'step-4': false
        },


    },
    mounted: function () {
        this.generate_image_code();
    },
    methods: {
        // 生成uuid
        generate_uuid: function () {
            var d = new Date().getTime();
            if (window.performance && typeof window.performance.now === "function") {
                d += performance.now(); //use high-precision timer if available
            }
            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
                var r = (d + Math.random() * 16) % 16 | 0;
                d = Math.floor(d / 16);
                return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
            });
            return uuid;
        },
        check_username: function () {
            if (!this.username) {
                this.error_username = true;
                this.error_username_message = "请填写用户名或手机号";
            } else {
                this.error_username = false;
            }
        },
        check_image_code: function () {
            if (!this.image_code) {
                this.error_image_code = true;
                this.error_image_code_message = '请填写验证码';
            } else {
                this.error_image_code = false;
            }
        },
        check_sms_code: function () {
            if (!this.sms_code) {
                this.error_sms_code = true;
                this.error_sms_code_message = '请填写短信验证码';
            } else {
                this.error_sms_code = false;
            }
        },
        check_pwd: function () {
            var len = this.password.length;
            if(len<8 || len>20){
                this.error_pwd_message = "仅允许8~20个字符的密码";
                this.error_password = true;
            }
            else {
                this.error_password = false;
            }
        },
        check_cpwd: function () {
            if(this.password === this.password2){
                this.error_check_password = false;
            }
            else {
                this.error_check_password = true;
                this.error_check_pwd_message = "两次输入的密码不一致"
            }
        },
        generate_image_code: function () {
            this.image_code_id = this.generate_uuid();
            this.image_code_url = this.host + "image_codes/" + this.image_code_id + "/";
        },
        send_sms_code: function () {
            if(this.sending_flag){
                return
            }
            this.sending_flag = true;
            axios.get(this.host + 'sms_codes/?access_token=' + this.access_token, {
                responseType: 'json'
            })
                .then(response =>{
                   // 设置一个定时器,倒计时
                   var num = 60
                   var timer = setInterval(()=>{
                            if(num <= 1){
                                clearInterval(timer);
                                this.sending_flag = false;
                                this.sms_code_tip = "获取短信验证码"
                            }
                            else{
                                num -= 1;
                                this.sms_code_tip = num + "秒";
                            }
                       }, 1000)
                })
                .catch(error=>{
                    alert(error.response.data.message);
                    this.sending_flag = false;
                })
        },
        form_1_on_submit: function () {
            this.check_username();
            this.check_image_code();
            if (!this.error_username && !this.error_image_code) {
                axios.get(this.host + "accounts/" + this.username + "/sms/token/?text=" +
                    this.image_code + "&image_code_id=" + this.image_code_id, {
                    responseType: 'json',
                })
                    .then(response => {
                        this.mobile = response.data.mobile;
                        this.access_token = response.data.access_token;
                        this.step_class['step-2'] = true;
                        this.step_class['step-1'] = false;
                        this.is_show_form_1 = false;
                        this.is_show_form_2 = true;
                    })
                    .catch(error => {
                        if(error.response.status === 400){
                            this.error_image_code_message = '验证码错误';
                            this.error_image_code = true;
                        }
                        else if(error.response.status === 404) {
                            this.error_username_message = "用户名或手机号不存在";
                            this.error_username = true
                        }
                        else {
                            console.log(error.response.data)
                        }
                        this.image_code = '';
                            this.generate_image_code();
                    })
            }

        },
        // 第二步表单提交,验证手机号的验证码,获取修改密码的access_token
        form_2_on_submit: function () {
            this.check_sms_code();
            if(!this.error_sms_code){
                axios.get(this.host + 'accounts/' + this.username + "/password/token/?sms_code=" + this.sms_code, {
                    responseType: 'json',
                })
                    .then(response=>{
                        this.user_id = response.data.user_id;
                        this.access_token = response.data.access_token;
                        this.step_class['step-3'] = true;
                        this.step_class['step-2'] = false;
                        this.is_show_form_3 = true;
                        this.is_show_form_2 = false;
                    })
                    .catch(error=>{
                        if(error.response.status === 400){
                            this.error_sms_code_message = "短息验证码错误"
                            this.error_sms_code = true;
                        }
                        else if(error.response.status === 404){
                            this.error_sms_code = true;
                            this.error_sms_code_message = "手机号不存在"
                        }
                        else {
                            alert(error.response.data.message);
                            console.log(error.response.data);
                        }
                    })
            }
        },
        form_3_on_submit: function () {
            this.check_pwd();
            this.check_cpwd();
            if(!this.error_password && !this.error_check_password){
                axios.post(this.host + 'users/' + this.user_id + '/password/',{
                    'password': this.password,
                    'password2': this.password2,
                    'access_token': this.access_token,
                }, {
                    responseType: 'json',
                })
                    .then(response=>{
                        this.step_class['step-4'] = true;
                        this.step_class['step-3'] = false;
                        this.is_show_form_3 = false;
                        this.is_show_form_4 = true;
                        // location.href = '/login.html'
                        // alert('密码修改成功,请重新登陆!')
                    })
                    .catch(error=>{
                        if(error.data.status === 400){
                            if("non_field_errors" in error.response.data){
                                this.error_pwd_message = error.response.data.non_field_errors[0];
                            }
                            else {
                                this.error_pwd_message = '数据有误';
                            }
                            this.error_password = true;
                        }
                        console.log(error.response.data);
                    })
            }
        },

    },
})