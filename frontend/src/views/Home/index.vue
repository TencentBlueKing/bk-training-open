<template>
    <div class="body">
        <div class="container">
            <div v-if="!yesterdayDaliy">
                <bk-alert type="warning" title="昨天的日报还没写！记得补上哦！" closable></bk-alert>
            </div>
            <div class="top_container">
                <span style="display: inline-block;margin-left:50px;">选择日期：</span>
                <bk-date-picker class="mr15" v-model="reportDate"
                    :clearable="false"
                    placeholder="选择日期"
                    :options="customOption"
                    @change="changeDate(reportDate)"
                >
                </bk-date-picker>
                <div>
                    <h2 class="mr30 f20" style="margin: 0;">
                        日报状态：
                        <span v-if="hasWrittenToday" style="color: #3A84FF;font-size: 18px;">已写日报</span>
                        <span v-else style="color: #63656E;font-size: 18px;">未写日报</span>
                    </h2>
                </div>
                <bk-button :theme="hasWrittenToday ? 'warning' : 'primary' " style="display: inline-block" @click="saveDaily" class="mr30">
                    {{ hasWrittenToday ? '修改' : '保存' }}
                </bk-button>
                <bk-button theme="success" style="display: inline-block" @click="moreTemplateDialog.visible = true">
                    添加模板
                </bk-button>
            </div>
            <div class="bottom_container">
                <template v-for="(singleContent, index) in dailyDataContent">
                    <div :key="index">
                        <div style="display: flex;justify-content: space-between;margin: 10px 0">
                            <h2 contenteditable="true" @input="changeTitleText(index)" :ref="'title' + index" style="display: inline-block;margin: 0">{{singleContent.title}}</h2>
                            <bk-button style="display: inline-block" theme="primary" @click="dealAdd(index)">
                                新增一条内容
                            </bk-button>
                        </div>
                        <div>
                            <bk-table
                                style="margin-top: 15px;"
                                :data="singleContent.content"
                                :virtual-render="true"
                                height="175px">
                                <bk-table-column prop="text" label="内容"></bk-table-column>
                                <bk-table-column width="150" prop="cost" label="所花时间"></bk-table-column>
                                <bk-table-column label="操作" width="150">
                                    <template slot-scope="props">
                                        <bk-button
                                            theme="warning"
                                            text
                                            @click="changeContent(props.row, index)">
                                            修改
                                        </bk-button>
                                        <bk-button
                                            theme="danger"
                                            text
                                            @click="deleteContent(props.row, index)">
                                            删除
                                        </bk-button>
                                    </template>
                                </bk-table-column>
                            </bk-table>
                        </div>
                    </div>
                </template>
                <bk-dialog
                    v-model="addDialog.visible"
                    title="新增内容"
                    :header-position="addDialog.headerPosition"
                    :width="addDialog.width"
                    @value-change="addDialogChange"
                    :position="{ top: 20, left: 100 }">
                    <div>
                        <h3>内容</h3>
                        <bk-input
                            placeholder="新内容"
                            type="textarea"
                            :rows="3"
                            v-model="newContent"
                        >
                        </bk-input>
                        <div style="display: flex;justify-content: space-between;margin: 10px 0">
                            <h3 style="margin: 0">所花时间</h3>
                            <div>
                                <span class="mr10 f10">隐私模式</span>
                                <bk-switcher v-model="isPrivate" class="mr30"></bk-switcher>
                            </div>
                        </div>
                        <bk-input
                            placeholder="所花时间"
                            type="number"
                            v-model="newCost"
                            :precision="1"
                            :min="0"
                        >
                            <template slot="append">
                                <div class="group-text">小时</div>
                            </template>
                        </bk-input>
                    </div>
                    <div slot="footer" class="dialog-foot">
                        <div>
                            <bk-button v-if="isAdd" theme="primary" title="分享" @click="addRow(currentIndex)">
                                添加
                            </bk-button>
                            <bk-button v-else theme="primary" title="分享" @click="changeRow(currentIndex)">
                                修改
                            </bk-button>
                        </div>
                    </div>
                </bk-dialog>
                <bk-dialog
                    v-model="moreTemplateDialog.visible"
                    :header-position="moreTemplateDialog.headerPosition"
                    :width="moreTemplateDialog.width"
                    @value-change="moreTemplateDialogChange"
                    :position="{ top: 20, left: 100 }">
                    <div slot="header">
                        <span class="mr30">新增模板标题</span>
                    </div>
                    <div>
                        <bk-input
                            placeholder="新增模板标题"
                            type="text"
                            v-model="newTitle"
                        >
                        </bk-input>
                    </div>
                    <div slot="footer" class="dialog-foot">
                        <div>
                            <bk-button theme="primary" title="添加" @click="addTemplate">
                                添加
                            </bk-button>
                        </div>
                    </div>
                </bk-dialog>
            </div>
            <template v-for="(tem,index) in newTemplateContent">
                <div :key="index">
                    <div style="display: flex;justify-content: space-between;margin: 10px 0">
                        <h2 style="display: inline-block;margin: 0">{{tem.title}}</h2>
                        <bk-button v-if="index > 0" style="display: inline-block" theme="primary" @click="deleteTemplate(index)">
                            删除该模板
                        </bk-button>
                    </div>
                    <bk-input
                        placeholder="请输入"
                        type="textarea"
                        :rows="3"
                        v-model="tem.text"
                    >
                    </bk-input>
                </div>
            </template>
        </div>
    </div>
</template>

<script>
    import moment from 'moment'
    import { bkAlert } from 'bk-magic-vue'

    export default {
        components: {
            bkAlert
        },
        data () {
            return {
                yesterdayDaliy: true,
                curDate: new Date(),
                reportDate: new Date(),
                formatDate: '',
                addDialog: {
                    visible: false,
                    width: 600,
                    headerPosition: 'left'
                },
                moreTemplateDialog: {
                    visible: false,
                    width: 600,
                    headerPosition: 'left'
                },
                // 此次操作是增加一列还是修改一列
                isAdd: true,
                // 修改指定行的临时变量
                targetRow: 0,
                // 日报信息
                dailyDataTitle: ['今日任务', '明日计划'],
                dailyDataContent: [
                    { 'title': '今日任务', 'type': 'table', 'content': [] },
                    { 'title': '明日计划', 'type': 'table', 'content': [] }
                ],
                isPrivate: false,
                dailyDates: [],
                // 新的内容和新花费时间的临时变量
                newContent: '',
                newCost: 0,
                // 新的模板标题及内容数组
                newTemplateContent: [
                    { 'title': '感想', 'type': 'text', 'text': '' }
                ],
                // 新标题临时变量
                newTitle: '',
                // 指向dailyData.content的下标
                currentIndex: 0,
                // 提交数据的格式化对象
                newPostDaily: {
                    date: null,
                    content: [],
                    template_id: 0,
                    send_email: false
                },
                // 今日写日报状况（已写，未写）
                hasWrittenToday: false,
                customOption: {
                    disabledDate: function (date) {
                        if (date > new Date()) {
                            return true
                        }
                    }
                }
            }
        },
        created () {
            this.formatDate = moment(new Date()).format(moment.HTML5_FMT.DATE)
            const dateInURL = this.$route.query.date
            if (dateInURL !== undefined) {
                this.reportDate = new Date(dateInURL)
                this.formatDate = dateInURL
            } else {
                this.reportDate = new Date()
            }
            this.init()
        },
        methods: {
            changeDate (date) {
                this.formatDate = moment(date).format(moment.HTML5_FMT.DATE)
                this.getDailyReport()
            },
            cheakDailyDates () {
                this.$http.get('/get_reports_dates/').then(res => {
                    if (res.result) {
                        this.dailyDates = res.data
                        this.customOption = {
                            disabledDate: (date) => {
                                if (moment(date).format('YYYY-MM-DD') !== moment(new Date()).format('YYYY-MM-DD') && (this.dailyDates.includes(moment(date).format('YYYY-MM-DD')) || date > new Date())) {
                                    return true
                                }
                            }
                        }
                    } else {
                        this.$bkMessage({
                            offsetY: 80,
                            message: res.message,
                            theme: 'error'
                        })
                    }
                })
            },
            changeTemplate () {
                if (this.curTemplateId === null || this.curTemplateId === '') {
                    this.curTemplate = []
                    this.dailyData = []
                }
            },
            checkYesterdayDaliy () {
                this.$http.get(
                    '/check_yesterday_daliy/'
                ).then(res => {
                    this.yesterdayDaliy = !!res.data
                })
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
                this.cheakDailyDates()
                this.getDailyReport()
                this.checkYesterdayDaliy()
            },
            getDailyReport () {
                this.$http.get(
                    '/daily_report/?date=' + this.formatDate
                ).then(res => {
                    if (Object.keys(res.data).length) {
                        this.hasWrittenToday = true
                        this.dailyDataTitle = []
                        this.dailyDataContent = []
                        this.newTemplateContent = []
                        for (const singleContent of res.data.content) {
                            if (singleContent.type === 'table') {
                                this.dailyDataTitle.push(singleContent.title)
                                this.dailyDataContent.push(singleContent)
                            } else {
                                this.newTemplateContent.push((singleContent))
                            }
                        }
                    } else {
                        //   重新初始化
                        this.hasWrittenToday = false
                        this.dailyDataTitle = ['今日任务', '明日计划']
                        this.dailyDataContent = [
                            { 'title': '今日任务', 'type': 'table', 'content': [] },
                            { 'title': '明日计划', 'type': 'table', 'content': [] }
                        ]
                        this.newTemplateContent = [
                            { 'title': '感想', 'type': 'text', 'text': '' }
                        ]
                    }
                    this.cheakDailyDates()
                })
            },
            // 改变默认模板标题
            changeTitleText (index) {
                const title = 'title' + index
                this.dailyDataTitle[index] = this.$refs[title][0].innerText
            },
            // 打开dialog, 增加一行
            dealAdd (index) {
                this.currentIndex = index
                this.isAdd = true
                this.addDialog.visible = true
            },
            // 保存增加表格中的一行新内容
            addRow (index) {
                const newObj = { 'text': this.newContent, 'cost': this.newCost + '小时', 'isPrivate': this.isPrivate }
                this.dailyDataContent[index]['content'].push(newObj)
                this.addDialog.visible = false
            },
            // 保存对指定行的修改
            changeRow (index) {
                const newObj = { 'text': this.newContent, 'cost': this.newCost + '小时', 'isPrivate': this.isPrivate }
                this.dailyDataContent[index]['content'].splice(this.targetRow, 1, newObj)
                this.addDialog.visible = false
            },
            // 打开dailog,改变表格中指定行内容
            changeContent (row, changeIndex) {
                this.currentIndex = changeIndex
                this.newContent = row.text
                this.newCost = parseFloat(row.cost)
                this.targetRow = row.$index
                this.isAdd = false
                this.addDialog.visible = true
            },
            // 删除表格中的一行内容
            deleteContent (row, removeIndex) {
                this.dailyDataContent[removeIndex]['content'].splice(row.$index, 1)
                this.$bkMessage({
                    theme: 'success',
                    message: '移除成功'
                })
            },
            // 保存日报
            saveDaily () {
                this.newPostDaily.date = this.formatDate
                for (const index in this.dailyDataContent) {
                    this.dailyDataContent[index].title = this.dailyDataTitle[index]
                }
                for (const tableContent of this.dailyDataContent) {
                    this.newPostDaily.content.push(tableContent)
                }
                for (const textContent of this.newTemplateContent) {
                    this.newPostDaily.content.push(textContent)
                }
                this.$http.post(
                    '/daily_report/', this.newPostDaily
                ).then(res => {
                    this.hasWrittenToday = true
                    this.newPostDaily = {
                        date: null,
                        content: [],
                        template_id: 0,
                        send_email: false
                    }
                    this.$bkMessage({
                        theme: 'success',
                        message: res.message
                    })
                })
            },
            // 增加自定义模板标题
            addTemplate () {
                this.newTemplateContent.push({ 'title': this.newTitle, 'type': 'text', 'text': '' })
                this.moreTemplateDialog.visible = false
            },
            // 删除自定义模板标题
            deleteTemplate (index) {
                this.newTemplateContent.splice(index, 1)
            },
            addDialogChange (val) {
                if (val === false) {
                    this.newContent = ''
                    this.newCost = 0
                }
            },
            moreTemplateDialogChange (val) {
                if (val === false) {
                    this.newTitle = ''
                }
            }
        }
    }
</script>

<style scoped>
.body{
    border: 2px solid #EAEBF0 ;
    margin:0px 100px;
    padding: 20px 50px;
    min-height: 80vh;
}
.demo-block.demo-alert .bk-alert{
    margin-bottom: 20px;
}
.top_container{
    width: 100%;
    padding: 10px 0;
    display: flex;
    justify-content: flex-end;
}
.bottom_container{
    width: 100%;
    padding-top: 20px;
}
::-webkit-scrollbar{
    display: none;
}
</style>
