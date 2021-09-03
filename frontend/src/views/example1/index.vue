<template>
    <div class="example1-wrapper">
        <div class="inner">
            <div class="item">
                <p>获取 user 信息</p>
                <bk-button type="default" @click="getUser">getUser</bk-button>
            </div>
            <div class="item">
                <p>{{userInfo}}</p>
            </div>
        </div>
        <div class="inner">
            <div class="item">
                <p>发送get请求</p>
                <bk-button type="default" @click="sendGet">get</bk-button>
            </div>
            <div class="item">
                <p>{{getMsg}}</p>
            </div>
        </div>
        <div class="inner">
            <div class="item">
                <p>获取 post 信息</p>
                <bk-button type="default" @click="sendPost">post</bk-button>
            </div>
            <div class="item">
                <p>{{postMsg}}</p>
            </div>
        </div>
    </div>
</template>

<script>
    export default {
        components: {
        },
        data () {
            return {
                getMsg: '',
                postMsg: '',
                userInfo: null
            }
        },
        created () {
        },
        methods: {
            /**
             * 获取页面数据
             *
             * @return {Promise} promise 对象
             */
            fetchPageData () {

            },

            /**
             * getUser
             */
            async getUser () {
                try {
                    const data = await this.$store.dispatch('userInfo', {}, { fromCache: true })
                    this.userInfo = Object.assign({}, data)
                } catch (e) {
                    console.error(e)
                }
            },
            /**
             * sendGet
             */
            sendGet () {
                this.$http.get('/send_get_or_post_test/').then(res => {
                    this.getMsg = res.message
                })
            },
            /**
             * sendPost
             */
            sendPost () {
                this.$http.post('/send_get_or_post_test/').then(res => {
                    this.postMsg = res.message
                })
            }
        }
    }
</script>

<style scoped>
    @import './index.css';
</style>
