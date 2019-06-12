var vm = new Vue({
    el: '#app',
    data: {
        host,
        username: '',  // 用户名
        password: '',  // 密码
        error_pwd_message: '请填写密码',
        error_username_message: '请输入用户名或手机号',

        error_username: false,  // 用户名输入错误标志
        error_password: false,  // 密码输入错误标志
        remember: false,  // 是否勾选记住登录
    },
    methods: {
        // 获取url路径参数
        get_query_string: function (name) {
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');
            var r = window.location.search.substr(1).match(reg);
            if (r != null) {
                return decodeURI(r[2]);
            }
            return null;
        },
        check_username: function () {
            this.error_username = !this.username;
        },
        check_password: function () {
            if (this.password) {
                this.error_password = false;
            } else {
                this.error_password = true;
                this.error_pwd_message = "请填写密码";
            }
        },
        on_submit: function () {
            this.check_username();
            this.check_password();
            if (!this.error_password && !this.error_username) {
                axios.post(this.host + 'authorizations/', {
                    username: this.username,
                    password: this.password,
                }, {
                    responseType: 'json',
                    withCredentials: true,
                })
                    .then(response => {
                        if(this.remember){
                            // 勾选了记住登录
                            sessionStorage.clear();
                            localStorage.username = response.data.username;
                            localStorage.user_id = response.data.id;
                            localStorage.token = response.data.token;
                        }
                        else{
                            // 未记住登录
                            localStorage.clear();
                            sessionStorage.token = response.data.token;
                            sessionStorage.user_id = response.data.user_id;
                            sessionStorage.username = response.data.username;
                        }
                        // 跳转页面
                        var return_url = this.get_query_string('next');
                        if (!return_url) {
                            return_url = '/index.html';
                        }
                        location.href = return_url;
                    })
                    .catch(error=>{
                        // console.log("捕获到错误")
                        if (error.response.status === 400) {
                            this.error_pwd_message = '用户名或密码错误';

                        } else {
                            this.error_pwd_message = '服务器错误';
                        }
                        this.error_password = true;
                    })
            }
        },
        qq_login: function () {
            var next = this.get_query_string('next') || '/';
            axios.get(this.host + "oauth/qq/authorization/?next=" + next, {
                responseType: 'json'
            })
                .then(response => {
                    location.href = response.data.oauth_url;
                })
                .catch(error => {
                    console.log(error.response.data);
                })
        }
    },
})