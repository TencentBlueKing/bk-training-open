<template>
    <div class="body">
        <div class="container">
            <div v-if="!yesterdayDaliy">
                <bk-alert type="warning" title="昨天的日报还没写！记得补上哦！" closable></bk-alert>
            </div>
            <div class="top_container">
                <bk-button theme="primary" style="display: inline-block" @click="clickLeaveManage">
                    请假管理
                </bk-button>
                <div>
                    <span style="display: inline-block;" class="f16">选择日期：</span>
                    <bk-date-picker
                        v-model="reportDate"
                        :clearable="false"
                        placeholder="选择日期"
                        :options="customOption"
                        @change="changeDate(reportDate)"
                        :shortcuts="shortcuts"
                        :shortcut-close="true"
                    >
                    </bk-date-picker>
                </div>
                <div style="padding: 5px 0">
                    <p style="margin: 0;">
                        <span>日报状态：</span>
                        <span v-if="hasWrittenToday" style="color: #3A84FF">已写日报</span>
                        <span v-else style="color: #63656E">未写日报</span>
                    </p>
                </div>
                <div style="padding: 4px 0 6px">
                    <span class="mr10">隐私模式</span>
                    <bk-switcher
                        v-model="allPrivate"
                        @change="setAllPrivate"
                    >
                    </bk-switcher>
                </div>
                <bk-sideslider
                    width="600"
                    :is-show.sync="leaveSetting.visible"
                    :quick-close="true"
                    @hidden="hiddenSlider"
                    direction="right"
                    ext-cls="leave-slide">
                    <div slot="header" class="slide-header">
                        <div :class="{
                            'header-tabs': true,
                            'tabs-active': title === activeTabTitle
                        }" v-for="(title,tindex) in slideTitleList" :key="tindex" @click="changeTab(title)">
                            {{title}}
                        </div>
                    </div>
                    <div slot="content">
                        <div class="leave-body" style="height: 530px;padding: 30px 0 0 10px;" v-show="activeTabTitle === slideTitleList[0]">
                            <div class="leave-apply">
                                <bk-form :label-width="80" form-type="horizontal">
                                    <bk-form-item label="请假日期" :required="true">
                                        <bk-date-picker
                                            v-model="leaveFormData.dateTimeRange"
                                            class="mr15"
                                            :clearable="false"
                                            placeholder="选择日期范围"
                                            type="daterange"
                                            :options="customLeaveOption"
                                            @clear="clearDate"
                                        ></bk-date-picker>
                                    </bk-form-item>
                                    <bk-form-item label="请假原因">
                                        <bk-input
                                            placeholder=""
                                            type="textarea"
                                            :rows="3"
                                            :maxlength="255"
                                            v-model="leaveFormData.reason">
                                        </bk-input>
                                    </bk-form-item>
                                    <bk-form-item class="mt20">
                                        <bk-button
                                            style="margin-right: 3px;"
                                            theme="primary" title="提交"
                                            @click.stop.prevent="submitLeave">提交</bk-button>
                                    </bk-form-item>
                                </bk-form>
                            </div>
                        </div>
                        <div class="leave-body" style="padding: 30px 10px 0;" v-show="activeTabTitle === slideTitleList[1]">
                            <div class="leave-manage">
                                <div class="select-bar">
                                    <div class="ptitle">选择组</div>
                                    <bk-select :disabled="false" v-model="selectedGroup" style="width: 200px;"
                                        ext-cls="select-custom"
                                        ext-popover-cls="select-popover-custom"
                                        @selected="handleSelectGroup"
                                        searchable>
                                        <bk-option v-for="goption in groupList"
                                            :key="goption.id"
                                            :id="goption.id"
                                            :name="goption.name">
                                        </bk-option>
                                    </bk-select>
                                </div>
                                <div class="leave-load" v-show="isleaveTableLoad" v-bkloading="{ isLoading: isleaveTableLoad, theme: 'primary', zIndex: 10 }"></div>
                                <bk-table
                                    v-show="!isleaveTableLoad"
                                    :virtual-render="false"
                                    :data="leaveTableData.data"
                                    :size="leaveTableData.size"
                                    :outer-border="false"
                                    :header-border="false"
                                    :header-cell-style="{ background: '#fff' }"
                                    @page-change="handlePageChange"
                                    @page-limit-change="handlePageLimitChange">
                                    <div slot="empty-text">
                                        空数据
                                    </div>
                                    <bk-table-column label="人员信息" prop="info" min-width="150" show-overflow-tooltip="true"></bk-table-column>
                                    <bk-table-column label="请假时间" prop="leaveDate" min-width="180" show-overflow-tooltip="true"></bk-table-column>
                                    <bk-table-column label="请假理由" prop="reason" min-width="100" show-overflow-tooltip="true"></bk-table-column>
                                    <bk-table-column label="操作" width="66">
                                        <template slot-scope="props">
                                            <bk-button class="mr10" theme="primary" text @click="removeLeave(props.row)">删除</bk-button>
                                        </template>
                                    </bk-table-column>
                                </bk-table>
                            </div>
                        </div>
                    </div>
                </bk-sideslider>
                <bk-button theme="primary" style="display: inline-block" @click="moreTemplateDialog.visible = true">
                    添加模板
                </bk-button>
            </div>
            <div class="bottom_container">
                <template v-for="(singleContent, index) in dailyDataContent">
                    <div :key="index" style="margin-bottom: 20px">
                        <div style="display: flex;justify-content: space-between;margin: 10px 0">
                            <h2 contenteditable="true" @input="changeTitleText(index)" :ref="'title' + index" style="display: inline-block;margin: 0">{{singleContent.title}}</h2>
                        </div>
                        <div>
                            <bk-table
                                style="margin-top: 15px;"
                                :data="singleContent.content"
                            >
                                <div slot="append" style="text-align: left;padding: 10px 15px">
                                    <bk-button style="display: inline-block;" text @click="dealAdd(index)">
                                        新增一条内容
                                    </bk-button>
                                </div>
                                <bk-table-column label="内容">
                                    <template slot-scope="props">
                                        <bk-input
                                            placeholder="新内容"
                                            v-model="singleContent.content[props.row.$index].text"
                                            type="textarea"
                                            :rows="3"
                                        >
                                        </bk-input>
                                    </template>
                                </bk-table-column>
                                <bk-table-column width="250" label="所花时间">
                                    <template slot-scope="props">
                                        <bk-input
                                            placeholder="所花时间"
                                            v-model="singleContent.content[props.row.$index].cost"
                                            type="number"
                                            :precision="1"
                                            :min="0"
                                            :max="24"
                                        >
                                            <template slot="append">
                                                <div class="group-text">小时</div>
                                            </template>
                                        </bk-input>
                                    </template>
                                </bk-table-column>
                                <bk-table-column width="100" label="隐私模式">
                                    <template slot-scope="props">
                                        <bk-switcher v-model="singleContent.content[props.row.$index].isPrivate"></bk-switcher>
                                    </template>
                                </bk-table-column>
                                <bk-table-column label="操作" width="100">
                                    <template slot-scope="props">
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
                    v-model="moreTemplateDialog.visible"
                    :header-position="moreTemplateDialog.headerPosition"
                    :width="moreTemplateDialog.width"
                    @value-change="moreTemplateDialogChange">
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
                <div :key="index" style="margin-top: 20px">
                    <div style="display: flex;justify-content: space-between;margin: 10px 0">
                        <h2 style="display: inline-block;margin: 0">{{tem.title}}</h2>
                        <bk-button v-if="index > 0" style="display: inline-block" text @click="deleteTemplate(index)">
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
            <div class="saveBtn">
                <bk-button :theme="hasWrittenToday ? 'warning' : 'primary' " style="display: inline-block" @click="saveDaily">
                    {{ hasWrittenToday ? '修改' : '保存' }}
                </bk-button>
            </div>
        </div>
    </div>
</template>

<script>
    import moment from 'moment'
    import {
        bkAlert,
        bkButton,
        bkDatePicker,
        bkForm,
        bkFormItem,
        bkInput,
        bkSideslider,
        bkTable,
        bkTableColumn
    } from 'bk-magic-vue'

    export default {
        name: '',
        components: {
            bkInput,
            bkDatePicker,
            bkTable,
            bkTableColumn,
            bkButton,
            bkSideslider,
            bkForm,
            bkFormItem,
            bkAlert
        },
        data () {
            return {
                shortcuts: [
                    {
                        text: '今天',
                        value () {
                            return new Date()
                        }
                    }
                ],
                yesterdayDaliy: true,
                curDate: new Date(),
                reportDate: new Date(),
                formatDate: '',
                moreTemplateDialog: {
                    visible: false,
                    width: 600,
                    headerPosition: 'left'
                },
                // 修改指定行的临时变量
                targetRow: 0,
                // 日报信息
                dailyDataTitle: ['今日任务', '明日计划'],
                dailyDataContent: [
                    { 'title': '今日任务', 'type': 'table', 'content': [] },
                    { 'title': '明日计划', 'type': 'table', 'content': [] }
                ],
                allPrivate: true,
                dailyDates: [],
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
                },
                leaveSetting: {
                    visible: false
                },
                isleaveTableLoad: true,
                leaveTableData: {
                    size: 'small',
                    data: [],
                    isAdmin: false
                },
                leaveFormData: {
                    reason: '',
                    dateTimeRange: [new Date(), new Date()]
                },
                slideTitleList: [
                    '请假申请',
                    '请假信息'
                ],
                activeTabTitle: '请假申请',
                groupList: [],
                selectedGroup: -1,
                customLeaveOption: {
                    disabledDate: function (date) {
                        const nowDate = new Date()
                        if (date < nowDate.setHours(nowDate.getHours() - 24)) {
                            return true
                        }
                    }
                },
                curUserLeaveList: []
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
        activated () {
            // 如果没有加入任何组就跳转到我的小组页面
            if (!this.groupList.length) {
                this.$http.get(
                    '/get_user_groups/'
                ).then(res => {
                    if (res.result) {
                        // 没有加入任何组就跳转到我的小组页面
                        if (res.data.length === 0) {
                            this.$router.push({ name: 'MyGroup' })
                        }
                    } else {
                        this.$bkMessage({
                            theme: 'error',
                            message: res.message
                        })
                    }
                })
            }
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
                    this.yesterdayDaliy = res.result
                })
            },
            // 界面初始化
            init () {
                this.cheakDailyDates()
                this.getDailyReport()
                // 获取当前用户组信息
                this.$http.get('/get_user_groups/').then((res) => {
                    if (res.result) {
                        if (res.data.length !== 0 && res.data.length !== null) {
                            this.groupList = res.data
                            if (this.groupList.length !== 0 && this.groupList.length !== undefined) {
                                this.selectedGroup = this.groupList[0].id
                            }
                        } else {
                            this.groupList = []
                            this.$router.push({ name: 'MyGroup' })
                        }
                    } else {
                        this.$bkMessage({
                            theme: 'error',
                            message: res.message
                        })
                    }
                })
                this.checkYesterdayDaliy()
            },
            setAllPrivate (val) {
                for (const item of this.dailyDataContent) {
                    for (const itemContent of item.content) {
                        itemContent.isPrivate = val
                    }
                }
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
                                this.newTemplateContent.push(singleContent)
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
                })
            },
            // 改变默认模板标题
            changeTitleText (index) {
                const title = 'title' + index
                this.dailyDataTitle[index] = this.$refs[title][0].innerText
            },
            // 打开dialog, 增加一行
            dealAdd (index) {
                const contentLength = this.dailyDataContent[index].content.length
                if (contentLength && !this.dailyDataContent[index].content[contentLength - 1].text) {
                    this.$bkMessage({
                        theme: 'warning',
                        message: '前一条内容为空'
                    })
                } else {
                    const newobj = { 'text': '', 'cost': 0, 'isPrivate': this.allPrivate, '$index': contentLength }
                    this.dailyDataContent[index].content.push(newobj)
                }
            },
            // 删除表格中的一行内容
            deleteContent (row, removeIndex) {
                this.dailyDataContent[removeIndex]['content'].splice(row.$index, 1)
                for (const itemContent of this.dailyDataContent[removeIndex]['content']) {
                    if (row.$index < itemContent.$index) {
                        itemContent.$index--
                    }
                }
                console.log('row.$index', row.$index)
                this.$bkMessage({
                    theme: 'success',
                    message: '移除成功'
                })
            },
            // 保存日报
            saveDaily () {
                let hasSomeContentEmpty = false
                const emptyContent = []
                this.newPostDaily.date = this.formatDate
                for (const index in this.dailyDataContent) {
                    this.dailyDataContent[index].title = this.dailyDataTitle[index]
                }
                for (const tableContent of this.dailyDataContent) {
                    const contentLength = tableContent.content.length
                    if (contentLength) {
                        if (!tableContent.content[contentLength - 1].text) {
                            hasSomeContentEmpty = true
                            emptyContent.push(tableContent.title + '最后一条')
                        } else {
                            for (const tableContentItem of tableContent.content) {
                                tableContentItem.cost = parseFloat(tableContentItem.cost)
                            }
                            this.newPostDaily.content.push(tableContent)
                        }
                    } else {
                        hasSomeContentEmpty = true
                        emptyContent.push(tableContent.title)
                    }
                }
                for (const textContent of this.newTemplateContent) {
                    if (!textContent.text.length) {
                        hasSomeContentEmpty = true
                        emptyContent.push(textContent.title)
                    }
                    this.newPostDaily.content.push(textContent)
                }
                if (!hasSomeContentEmpty) {
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
                } else {
                    this.$bkMessage({
                        theme: 'warning',
                        message: emptyContent.join(',') + ' 内容为空！'
                    })
                    this.newPostDaily.content = []
                }
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
            moreTemplateDialogChange (val) {
                if (val === false) {
                    this.newTitle = ''
                }
            },
            // 获取请假管理表
            getLeaveList (sign) {
                const groupId = this.selectedGroup
                if (sign === null || sign === undefined) {
                    sign = 0 // 1 返回未请假人 或 0 返回请假人 或 2 返回个人所有请假信息
                }

                if (groupId === -1) {
                    this.$bkMessage({
                        'offsetY': 80,
                        'delay': 2000,
                        'theme': 'warning',
                        'message': '用户当前未加入任何组，无请假信息。'
                    })
                } else {
                    const vm = this
                    this.isleaveTableLoad = true
                    this.leaveTableData.data = []
                    const todayDate = moment(new Date()).format(moment.HTML5_FMT.DATE)
                    this.$http.get('/display_personnel_information/' + groupId
                        + '/?date=' + todayDate
                        + '&sign=' + sign
                    ).then(res => {
                        if (res.result) {
                            if (res.data.length !== null && res.data.length !== 0) {
                                if (sign === 2) {
                                    this.curUserLeaveList = res.data
                                    // 设置请假日期选择栏禁用日期
                                    this.customLeaveOption = {
                                        disabledDate: function (date) {
                                            const nowDate = new Date()
                                            if (date < nowDate.setHours(nowDate.getHours() - 24)) {
                                                return true
                                            } else {
                                                let iscompareDateShow = true
                                                vm.curUserLeaveList.map((item, index) => {
                                                    const startDate = moment(item[0]).format('YYYY-MM-DD')
                                                    const compareDate = moment(date).format('YYYY-MM-DD')
                                                    const endDate = moment(item[1]).format('YYYY-MM-DD')
                                                    if (moment(startDate).isSameOrBefore(compareDate, 'day') && moment(compareDate).isSameOrBefore(endDate, 'day')) {
                                                        iscompareDateShow = false
                                                    }
                                                })
                                                return !iscompareDateShow
                                            }
                                        }
                                    }
                                } else if (sign === 0) {
                                    res.data.map((item, index) => {
                                        this.leaveTableData.data.push({
                                            'offdayId': item.off_info.id,
                                            'leaveDate': item.off_info.start_date + '  ~  ' + item.off_info.end_date,
                                            'reason': item.off_info.reason,
                                            'info': item.username + '(' + item.name + ')',
                                            'username': item.username
                                        })
                                    })
                                }
                            }
                        } else {
                            this.$bkMessage({
                                'offsetY': 80,
                                'delay': 2000,
                                'theme': 'warning',
                                'message': res.message
                            })
                        }
                    }).finally(() => {
                        this.isleaveTableLoad = false
                    })
                }
            },
            // 请假滑窗关闭事件
            hiddenSlider () {
                this.leaveFormData.reason = ''
                this.leaveFormData.dateTimeRange = [new Date(), new Date()]
                this.activeTabTitle = '请假申请'
            },
            // 切换请假页签事件
            changeTab (title) {
                this.activeTabTitle = title
                if (this.activeTabTitle === '请假信息') {
                    this.getLeaveList()
                    this.getLeaveList(2)
                }
            },
            // 选择组
            handleSelectGroup (value, option) {
                this.getLeaveList()
                this.getLeaveList(2)
            },
            // 清空请假日期
            clearDate () {
                this.leaveFormData.dateTimeRange = -1
            },
            // 请假确认事件
            submitLeave () {
                if (this.leaveFormData.reason === '') {
                    this.$bkMessage({
                        'offsetY': 80,
                        'delay': 2000,
                        'theme': 'warning',
                        'message': '请填写请假原因'
                    })
                    return
                }
                const params = {}
                params.start_date = moment(this.leaveFormData.dateTimeRange[0]).format(moment.HTML5_FMT.DATE)
                params.end_date = moment(this.leaveFormData.dateTimeRange[1]).format(moment.HTML5_FMT.DATE)
                params.reason = this.leaveFormData.reason
                this.$http.post('/add_off_info/', params).then(res => {
                    if (res.result) {
                        this.$bkMessage({
                            'offsetY': 80,
                            'delay': 2000,
                            'theme': 'success',
                            'message': res.message
                        })
                        this.getLeaveList(2)
                    } else {
                        this.$bkMessage({
                            'offsetY': 80,
                            'delay': 2000,
                            'theme': 'warning',
                            'message': res.message
                        })
                    }
                })
            },
            // 请假管理按钮点击事件
            clickLeaveManage () {
                this.leaveSetting.visible = true
                this.getLeaveList(2)
            },
            // 删除请假信息
            removeLeave (row) {
                const groupId = this.selectedGroup
                const offdayId = row.offdayId
                const vm = this
                if (groupId === -1) {
                    this.$bkMessage({
                        'offsetY': 80,
                        'delay': 2000,
                        'theme': 'warning',
                        'message': '用户当前未加入任何组，无请假信息可删除。'
                    })
                } else {
                    this.$bkInfo({
                        title: '确认删除该请假信息？',
                        confirmLoading: true,
                        confirmFn: async () => {
                            try {
                                vm.$http.delete('/remove_off/' + groupId + '/' + offdayId + '/').then(res => {
                                    if (res.result) {
                                        vm.$bkMessage({
                                            'offsetY': 80,
                                            'delay': 2000,
                                            'theme': 'success',
                                            'message': res.message
                                        })
                                        vm.getLeaveList()
                                        vm.getLeaveList(2)
                                    } else {
                                        vm.$bkMessage({
                                            'offsetY': 80,
                                            'delay': 2000,
                                            'theme': 'warning',
                                            'message': res.message
                                        })
                                    }
                                })
                                return true
                            } catch (e) {
                                vm.$bkMessage({
                                    'offsetY': 80,
                                    'delay': 2000,
                                    'theme': 'warning',
                                    'message': '删除请假信息失败'
                                })
                                return false
                            }
                        }
                    })
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
        min-height: calc(100vh - 140px);
    }
    .demo-block.demo-alert .bk-alert{
        margin-bottom: 20px;
    }
    .top_container{
        width: 100%;
        padding: 10px 0;
        display: flex;
        justify-content: space-between;
    }
    .bottom_container{
        width: 100%;
        padding-top: 20px;
    }
    ::-webkit-scrollbar{
        display: none;
    }
    .saveBtn{
        display: flex;
        justify-content: flex-end;
        margin-top: 20px;
    }
    .leave-slide .slide-header{
            display: flex;
            flex-wrap: nowrap;
    }
    .leave-slide .slide-header .title{
        height: 60px;
        line-height: 60px;
        border-bottom: 1px solid #dcdee5;
        font-size: 16px;
        font-weight: 700;
        color: #666;
    }
    .leave-slide .slide-header .header-tabs{
        width: 50%;
        text-align:center
    }
    .leave-slide .slide-header .tabs-active{
        border-bottom: 2px solid #3a84ff;
        color: #3a84ff;
    }
    .leave-slide .slide-header .header-tabs:hover{
        cursor: pointer;
        color: #3a84ff;
    }
    .leave-slide .leave-manage .leave-load {
        height: 300px;
        line-height: 300px;
        text-align: center;
    }
    .leave-slide .leave-manage /deep/ .bk-table .bk-table-header-wrapper .bk-table-header{
        width: 100% !important;
    }
    .leave-slide .leave-manage /deep/ .bk-table .bk-table-body-wrapper .bk-table-body{
        width: 100% !important;
    }
    .leave-slide .leave-manage /deep/ .bk-table .bk-table-body-wrapper .bk-table-empty-block{
        width: 100% !important;
    }
    .bottom_container /deep/ .bk-table-empty-block{
        height: 0 !important;
        min-height: 0 !important;
        overflow: hidden;
    }
    .bottom_container /deep/ .bk-virtual-content{
      height: 100% !important;
    }
    .bottom_container /deep/ .bk-scroll-x{
        overflow-x: hidden !important;
    }
    .bottom_container /deep/ .bk-virtual-content{
        position: inherit !important;
    }
    .bottom_container /deep/ .bk-virtual-section{
        display: none !important;
    }
    .leave-slide .leave-manage .select-bar{
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        margin-bottom: 20px;
    }
    .leave-slide .leave-manage .select-bar .ptitle{
        font-size: 14px;
        font-weight: 400;
        color: #63656e;
        margin-right: 10px;
    }
    .leave-slide .leave-manage .loadbox{
        height: 300px;
        line-height: 300px;
        border: 1px solid #eee;
        text-align: center;
    }
    .leave-slide .leave-body .leave-apply .bk-form .bk-form-item .bk-form-content .bk-form-control{
        width: 94% !important;
    }
    .leave-slide .leave-body .leave-apply .bk-form .bk-form-item .bk-form-content .bk-date-picker{
        width: 200px;
    }
    .leave-slide .slide-header{
        display: flex;
        flex-wrap: nowrap;
    }
    .leave-slide .slide-header .title{
        height: 60px;
        line-height: 60px;
        border-bottom: 1px solid #dcdee5;
        font-size: 16px;
        font-weight: 700;
        color: #666;
    }
    .leave-slide .slide-header .header-tabs{
        width: 50%;
        text-align:center
    }
    .leave-slide .slide-header .tabs-active{
        border-bottom: 2px solid #3a84ff;
        color: #3a84ff;
    }
    .leave-slide .slide-header .header-tabs:hover{
        cursor: pointer;
        color: #3a84ff;
    }
    .leave-slide .leave-manage .leave-load {
        height: 300px;
        line-height: 300px;
        /* border: 1px solid #eee; */
        text-align: center;
    }
    .leave-slide .leave-manage .select-bar{
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        margin-bottom: 20px;
    }
    .leave-slide .leave-manage .select-bar .ptitle{
        font-size: 14px;
        font-weight: 400;
        color: #63656e;
        margin-right: 10px;
    }
    .leave-slide .leave-manage .loadbox{
        height: 300px;
        line-height: 300px;
        border: 1px solid #eee;
        text-align: center;
    }
    .leave-slide .leave-body .leave-apply .bk-form .bk-form-item .bk-form-content .bk-form-control{
        width: 94% !important;
    }
    .leave-slide .leave-body .leave-apply .bk-form .bk-form-item .bk-form-content .bk-date-picker{
        width: 200px;
    }
    .demo-block.demo-alert .bk-alert{
        margin-bottom: 20px;
    }
</style>
