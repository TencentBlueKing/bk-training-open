<template>
    <contentWapper :pageid="pageId" :minheight="pageMinHeight">
        <div class="addReport-body">
            <div class="top_container">
                <div class="fun-bar">
                    <div class="fun-item">
                        <span style="line-height: 32px;">选择模板：</span>
                        <bk-select :disabled="!writeFalg" v-model="curTemplateId"
                            class="select-template"
                            ext-cls="select-custom"
                            ext-popover-cls="select-popover-custom"
                            searchable
                            @selected="selectTemplate()"
                            @change="changeTemplate()"
                            placeholder="请选择模板"
                        >
                            <bk-option v-for="template in templateList"
                                :key="template.id"
                                :id="template.id"
                                :name="template.name">
                            </bk-option>
                        </bk-select>
                    </div>
                    <div class="fun-item">
                        <span>选择日期：</span>
                        <bk-date-picker class="mr15" v-model="reportDate"
                            :clearable="false"
                            :placeholder="'选择日期'"
                            :ext-popover-cls="'custom-popover-cls'"
                            :options="customOption"
                            @change="getDailyByDate(reportDate)"
                        >
                        </bk-date-picker>
                    </div>
                    <bk-button :theme="'primary'"
                        :disabled="!writeFalg"
                        type="submit" :title="'保存'" @click="clickSaveDaily()">
                        保存
                    </bk-button>
                </div>
                
                <div class="state-bar" style="justify-content: flex-end;">
                    <bk-dialog v-model="saveDailyDialog.visiable" theme="primary" class="save-daily-dialog" :show-footer="false">
                        <bk-form label-width="80">
                            <bk-form-item style="margin-left:60px;">
                                请选择保存方式
                            </bk-form-item>
                            <bk-form-item>
                                <bk-button style="margin-right: 20px;" theme="primary" title="保存并发送邮件" @click.stop.prevent="saveAndSend()">保存并发送邮件</bk-button>
                                <bk-button ext-cls="mr5" @click="saveDaily()" theme="default" title="仅保存">仅保存</bk-button>
                            </bk-form-item>
                        </bk-form>
                    </bk-dialog>
                    <span class="state-text">
                        日报状态：{{saveText}}
                    </span>
                </div>

            </div>

            <div v-show="reportIsLoading" class="test-dom" v-bkloading="{ isLoading: basicLoading, theme: 'primary', zIndex: 10 }">
            </div>
            <!-- 写日报模块 -->
            <div v-show="!reportIsLoading" class="body-container">
                <div v-for="(title,index) in curTemplate" :key="index" style="margin:50px 0px;">
                    <div style="font-size: 18px;font-weight: 700;">{{title}}</div>
                    <div class="input-demo">
                        <bk-input
                            placeholder=""
                            :type="'textarea'"
                            :rows="3"
                            :maxlength="255"
                            v-model="dailyData[index]"
                            :disabled="!writeFalg"
                            @change="saveFalg = true"
                        >
                        </bk-input>
                    </div>
                </div>
            </div>
            
        </div>
    </contentWapper>

</template>

<script>
    import contentWapper from '../components/content-wapper.vue'
    export default {
        name: '',
        components: {
            contentWapper
        },
        data () {
            return {
                pageId: 'addReport',
                pageMinHeight: 840,
                reportIsLoading: true,
                basicLoading: true,
                templateList: [],
                curTemplateId: null,
                curTemplate: [],
                // 日报内容
                dailyData: [],
                // 添加日报提交表单内容
                addDailyFormData: {
                    date: null,
                    content: {},
                    template_id: null,
                    send_email: false
                },
                reportDate: new Date(),
                customOption: {
                    disabledDate: function (date) {
                        if (date > new Date()) {
                            return true
                        }
                    }
                },
                saveDailyDialog: {
                    visiable: false
                },
                saveFalg: false,
                writeFalg: true,
                saveText: '未保存',
                clearFlag: 0
            }
        },
        created () {
            const vm = this
            vm.init()
        },
        methods: {
            // 转化日期格式yyyy-MM-dd
            formateDate (date) {
                return date.getFullYear() + '-' + (date.getMonth() >= 9 ? (date.getMonth() + 1) : '0' + (date.getMonth() + 1)) + '-' + (date.getDate() > 9 ? (date.getDate()) : '0' + (date.getDate()))
            },
            changeTemplate () {
                console.log(this.curTemplateId + 'x')
                if (this.curTemplateId === null || this.curTemplateId === '') {
                    this.curTemplate = []
                    this.dailyData = []
                }
            },
            // 切换模板
            selectTemplate () {
                this.dailyData = []
                const vm = this
                vm.templateList.forEach(function (template) {
                    if (template.id === vm.curTemplateId) {
                        vm.curTemplate = template.content.split(';')
                    }
                })
            },
            // 界面初始化
            init () {
                const vm = this
                // 开始loading
                vm.reportIsLoading = true
                
                this.$http.get('/get_all_report_template/').then(res => {
                    if (res.result) {
                        this.templateList = res.data
                        this.clearFlag = 1
                        // 获取用户今日的日报
                        this.getDailyByDate(this.reportDate)
                    } else {
                        // 调用获取日报模板接口失败
                        vm.reportIsLoading = false
                        const config = {}
                        config.offsetY = 80
                        config.message = res.message
                        config.theme = 'error'
                        this.$bkMessage(config)
                    }
                })
            },
            clickSaveDaily () {
                console.log('isToday', this.formateDate(this.reportDate) === this.formateDate(new Date()))
                if (this.formateDate(this.reportDate) === this.formateDate(new Date())) {
                    this.saveDaily()
                } else {
                    this.saveDailyDialog.visiable = true
                }
            },
            // 获取用户指定日期日报，如果没有写日报，则自动渲染第一个模板的内容
            getDailyByDate (date) {
                const vm = this
                this.writeFalg = true
                const config = {}
                config.offsetY = 80
                console.log('templates', this.templateList)
                this.$http.get('/daily_report/?date=' + this.formateDate(date))
                    .then(res => {
                        if (res.result) {
                            console.log('vm.reportIsLoading == ', vm.reportIsLoading)
                            console.log('daily', res.data)
                            if (JSON.stringify(res.data) === '{}') {
                                // 今天的日志还没写
                                if (this.templateList.length > 0) {
                                    // 默认选择第一个默认模板
                                    this.curTemplateId = this.templateList[0].id
                                    this.curTemplate = this.templateList[0].content.split(';')
                                    console.log('curTemplateId:', this.curTemplateId)
                                    console.log('curTemplate', this.curTemplate)
                                    this.dailyData = []
                                    this.saveText = '未保存'
                                }
                            } else {
                                // 写了日报，给日报注入内容
                                const templateContent = []
                                const daily = []
                                for (const key in res.data.content) {
                                    templateContent.push(key)
                                    daily.push(res.data.content[key])
                                }
                                this.curTemplateId = res.data.template_id
                                this.curTemplate = templateContent
                                this.dailyData = daily
                                console.log('curTemplateId', this.curTemplateId)
                                console.log('curTemplate', this.curTemplate)
                                console.log('dailyData', this.dailyData)
                                if (res.data.send_describe === '已发送') {
                                    this.writeFalg = false
                                }
                                this.saveText = res.data.send_describe
                            }
                        } else {
                            // 调用获取当前日报接口失败
                            vm.reportIsLoading = false
                            config.message = res.message
                            config.theme = 'error'
                            this.$bkMessage(config)
                        }
                    }).finally(() => {
                        vm.reportIsLoading = false
                    })
            },
            saveAndSend () {
                this.addDailyFormData.send_email = true
                this.saveDaily()
            },
            // 保存日报
            saveDaily () {
                // 消息提示框的参数设置
                const config = {
                    'offsetY': 80
                }
                if (this.dailyData.length === 0) {
                    config.message = '未填写内容不可以保存日报'
                    config.theme = 'error'
                    this.$bkMessage(config)
                    return
                }
                console.log(this.dailyData)
                let flag = true
                const content = {}
                for (let i = 0; i < this.curTemplate.length; i++) {
                    console.log('日报内容', this.dailyData[i])
                    if (this.dailyData[i] === null || this.dailyData[i] === '' || this.dailyData[i] === undefined) {
                        config.message = '"' + this.curTemplate[i] + '"不可为空'
                        flag = false
                    } else {
                        // 设置日期内容
                        content[this.curTemplate[i]] = this.dailyData[i]
                    }
                }
                console.log('hasFullContentFlag:', flag)
                if (flag === false) {
                    this.addDailyFormData = { date: null, content: {}, template_id: null }
                    config.theme = 'error'
                    this.$bkMessage(config)
                } else {
                    // 设置日期数据
                    this.addDailyFormData.date = this.formateDate(this.reportDate)
                    this.addDailyFormData.content = content
                    this.addDailyFormData.template_id = this.curTemplateId
                    // 调取添加日报接口
                    console.log('addDailyFormData:', this.addDailyFormData)
                    this.$http.post('/daily_report/', this.addDailyFormData).then(res => {
                        config.message = res.message
                        if (res.result) {
                            config.theme = 'success'
                            this.$bkMessage(config)
                            console.log('填写成功，重新获取日报信息')
                        } else {
                            this.addDailyFormData = null
                            config.theme = 'error'
                            this.$bkMessage(config)
                        }
                        this.getDailyByDate(this.reportDate)
                        this.saveDailyDialog.visiable = false
                        this.sendEmail = false
                    })
                }
            }

        }
    }
</script>

<style scoped>
    .test-dom {
        height: 300px;
        line-height: 300px;
        /* border: 1px solid #eee; */
        text-align: center;
    }
    .container-title {
        font-size: 22px;
        font-weight: 700;
    }
    .body-container {
        margin-top:40px;
    }
    .top_container{
        width: 100%;
        display: flex;
        flex-wrap: wrap;
        flex-wrap: wrap;
        justify-content: space-between;
    }
    .top_container /deep/ .bk-date-picker{
        width: 50%;
        position: relative;
        width: 110px;
    }
    .fun-bar{
        width: 700px;
        display: flex;
        justify-content: flex-start;
        flex-flow: wrap;
        flex-direction: row;
    }
    .fun-item{
        display: flex;
        height: 32px;
        line-height: 32px;
        margin-right: 20px;
    }
    .state-bar{
        display: flex;
        height: 32px;
        line-height: 32px;
    }
    .mr15 /deep/ .bk-date-picker-dropdown{
        top:32px !important;
    }
    .input-demo {
        margin-top:20px ;
    }
    .select-template{
        width: 12%;
        min-width: 100px;
        display: inline-block;
        vertical-align: bottom;
    }
    .state-text{
        margin-top: 8px;
        font-size: 16px;
    }
</style>
