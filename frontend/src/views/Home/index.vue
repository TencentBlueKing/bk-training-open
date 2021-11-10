<template>
    <div id="myDaily">
        <div class="body">
            <bk-divider align="left" style="margin-bottom:30px;">
                <div class="container_title">填写日报</div>
            </bk-divider>
            <div class="top_container" style="margin-top:50px;">
                <span>选择模板：</span>
                <bk-select :disabled="!writeFalg" v-model="curTemplateId" style="width: 250px; display: inline-block; vertical-align: bottom; "
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
                <span style="display: inline-block;margin-left:50px;">选择日期：</span>
                <bk-date-picker class="mr15" v-model="reportDate"
                    :clearable="false"
                    :placeholder="'选择日期'"
                    :ext-popover-cls="'custom-popover-cls'"
                    :options="customOption"
                    @change="getDailyByDate(reportDate)"
                >
                </bk-date-picker>
                <bk-button :theme="'primary'"
                    :disabled="!writeFalg"
                    type="submit" :title="'保存'" @click="saveDaily()" class="mr10" style="margin-left:40px;">
                    保存
                </bk-button>
                <span class="tag-view" style="display:inline-block; width:200px;">
                    <bk-tag id="saveTag" :theme="tagTheme">{{saveText}}</bk-tag>
                </span>

            </div>
            <!-- 写日报模块 -->
            <div class="body_container">
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
    </div>

</template>

<script>
    export default {
        name: '',
        data () {
            return {
                templateList: [],
                curTemplateId: null,
                curTemplate: [],
                // 日报内容
                dailyData: [],
                // 添加日报提交表单内容
                addDailyFormData: {
                    date: null,
                    content: {},
                    template_id: null
                },
                reportDate: new Date(),
                customOption: {
                    disabledDate: function (date) {
                        if (date > new Date()) {
                            return true
                        }
                    }
                },
                saveFalg: false,
                writeFalg: true,
                saveText: '未保存',
                clearFlag: 0
            }
        },
        created () {
            this.init()
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
                console.log('curTemplateId', this.curTemplateId)
                this.dailyData = []
                const vm = this
                vm.templateList.forEach(function (template) {
                    if (template.id === vm.curTemplateId) {
                        vm.curTemplate = template.content.split(';')
                    }
                })
                console.log('template', this.curTemplate)
                
                console.log('templates', this.templateList)
            },
            // 界面初始化
            init () {
                this.$http.get('/get_all_report_template/').then(res => {
                    if (res.result) {
                        this.templateList = res.data
                        this.clearFlag = 1
                        console.log('templateList', this.templateList)
                        // 获取用户今日的日报
                        this.getDailyByDate(this.reportDate)
                    } else {
                        // 调用获取日报模板接口失败
                        const config = {}
                        config.offsetY = 80
                        config.message = res.message
                        config.theme = 'error'
                        this.$bkMessage(config)
                    }
                })
            },
            // 获取用户指定日期日报，如果没有写日报，则自动渲染第一个模板的内容
            getDailyByDate (date) {
                this.writeFalg = true
                const config = {}
                config.offsetY = 80
                console.log('templates', this.templateList)
                this.$http.get('/daily_report/?date=' + this.formateDate(date)).then(res => {
                    if (res.result) {
                        console.log('daily', res.data)
                        if (JSON.stringify(res.data) === '{}') {
                            // 今天的日志还没写
                            console.log(this.formateDate(date) + '天没写日报')
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
                            if (res.data.send_describe === '邮件已发送小组成员查看') {
                                this.writeFalg = false
                            }
                            this.saveText = res.data.send_describe
                        }
                    } else {
                        // 调用获取当前日报接口失败
                        config.message = res.message
                        config.theme = 'error'
                        this.$bkMessage(config)
                    }
                })
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
                for (let i = 0; i < this.dailyData.length; i++) {
                    console.log('日报内容', this.dailyData[i])
                    if (this.dailyData[i].length === 0) {
                        config.message = '"' + this.curTemplate.content[i] + '"不可为空'
                        config.theme = 'error'
                        this.$bkMessage(config)
                        return
                    }
                    this.addDailyFormData.content[this.curTemplate[i]] = this.dailyData[i]
                }
                // 设置日期数据
                this.addDailyFormData.date = this.reportDate.getFullYear() + '-'
                    + (this.reportDate.getMonth() >= 9 ? (this.reportDate.getMonth() + 1) : '0' + (this.reportDate.getMonth() + 1)) + '-'
                    + (this.reportDate.getDate() > 9 ? (this.reportDate.getDate()) : '0' + (this.reportDate.getDate()))
                this.addDailyFormData.template_id = this.curTemplateId
                // 调取添加日报接口
                console.log('addDailyFormData:', this.addDailyFormData)
                this.$http.post('/daily_report/', this.addDailyFormData).then(res => {
                    config.message = res.message
                    if (res.result) {
                        config.theme = 'success'
                        this.$bkMessage(config)
                    } else {
                        this.addDailyFormData = null
                        config.theme = 'error'
                        this.$bkMessage(config)
                    }
                })
            }

        }
    }
</script>

<style scoped>
    .body {
        border: 2px solid #EAEBF0 ;
        width: 1649px;
        margin:0px 100px;
        padding: 20px 50px;
        min-height: 831px;
    }
    .container_title {
        font-size: 22px;
        font-weight: 700;
    }
    .body_container {
        margin-top:40px;
    }
    .input-demo {
        margin-top:20px ;
    }
</style>
