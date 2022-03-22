<template>
    <div class="groupdaily">
        <div class="groupdaily-btn">
            <div class="bk-button-group">
                <bk-button :class="curType === 'date' ? 'is-selected' : ''" size="small" @click="selectedType('date')">日期
                </bk-button>
                <bk-button :class="curType === 'member' ? 'is-selected' : ''" size="small" @click="selectedType('member')">成员
                </bk-button>
            </div>
            <!-- 成员选择器 -->
            <div class="groupdaily-member-select" v-show="curType === 'member'">
                <bk-select
                    :disabled="false"
                    v-model="curSelectUsername"
                    style="width: 250px;"
                    behavior="normal"
                    :clearable="false"
                    font-size="normal"
                    @selected="changeUser"
                    ext-popover-cls="select-popover-custom"
                    searchable>
                    <bk-option v-for="option in groupusers"
                        :key="option.id"
                        :id="option.username"
                        :name="option.username + '(' + option.name + ')'">
                    </bk-option>
                </bk-select>
                <FastBtn :top="top" :bottom="bottom" @topItem="topItem" @bottomItem="bottomItem" />
            </div>
            <!-- 日期选择器 -->
            <div class="groupdaily-date-select" v-show="curType === 'date'">
                <bk-date-picker font-size="normal" @change="changeDate" style="width: 250px;" :clearable="false"
                    v-model="curDateTime"></bk-date-picker>
                <FastBtn :time="time" @topItem="topItem" @bottomItem="bottomItem" />
            </div>
            <!-- 分割线 -->
            <div class="halving"></div>
        </div>
        <div class="group-time-box" style="float: right">
            <div class="time-box" style="height: 0px ">
                <div class="blue-background-time">
                    <div class="time-single ">
                    </div>
                </div>
                <div style="margin-left: 10px;font-size: 14px">开发时间</div>
                <div class="gray-background-time" style="margin-left: 10px;">
                    <div class="time-single ">
                    </div>
                </div>
                <div style="margin-left: 10px;font-size: 14px">其他时间</div>
            </div>
        </div>
        <div class="user-time-content-box" v-bkloading="{ isLoading: loading, zIndex: 10 }">
            <div class="user-time-content-box-first" v-show="curType === 'date'">
                <bk-table
                    :data="timeData"
                    :size="size"
                >
                    <bk-table-column label="成员" prop="username" width="240px"></bk-table-column>
                    <bk-table-column :render-header="() => {
                        return [1,2,3,4,5,6,7,8,9,10,11,12,13,14].map(item => {
                            return $createElement('div',{ style },item + 7)
                        })
                    }">
                        <template slot-scope="props">
                            <div class="group-time-box" style="padding: 0px">
                                <div class="time-box" style="margin-left: -10px">
                                    <div v-for="item in timeSplits" :key="item" class="time-single-box"
                                        :class="checkFreeTime(props.row.free_time, item)">
                                    </div>
                                </div>
                            </div></template>
                    </bk-table-column>
                </bk-table>
            </div>
            <div v-show="curType === 'member'">
                <bk-table
                    :data="timeData"
                    :size="size"
                >
                    <bk-table-column label="日期" width="100px">
                        <template slot-scope="props">
                            <div class="item-box">
                                <div :class="props.row.is_day ? 'focusitem' : ''"></div>
                                <div :style="props.row.is_day ? 'margin-left:-4px' : ''">
                                    {{ props.row.date}}
                                </div>
                            </div>
                        </template>
                    </bk-table-column>
                    <bk-table-column label="星期" prop="weekend" width="100px"></bk-table-column>
                    <bk-table-column :render-header="() => {
                        return [1,2,3,4,5,6,7,8,9,10,11,12,13,14].map(item => {
                            return $createElement('div',{ style },item + 7)
                        })
                    }">
                        <template slot-scope="props">
                            <div class="group-time-box" style="padding: 0px">
                                <div class="time-box" style="margin-left: -10px">
                                    <div v-for="item in timeSplits" :key="item" class="time-single-box"
                                        :class="checkFreeTime(props.row.free_time, item)">
                                    </div>
                                </div>
                            </div>
                        </template>
                    </bk-table-column>
                </bk-table>
            </div>
        </div></div></template>
<script>
    import moment from 'moment'
    import FastBtn from '@/components/GroupDailys/FastBtn'
    import { bkSelect, bkOption, bkDatePicker, bkButton } from 'bk-magic-vue'

    export default {
        components: {
            bkSelect,
            bkOption,
            bkDatePicker,
            bkButton,
            FastBtn
        },
        props: {
            // 当前组id
            curgroupid: {
                type: Number
            },
            groupusers: {
                type: Object
            },
            username: {
                type: String
            },
            refreshpage: {
                type: Boolean
            }
        },
        data () {
            return {
                style: { float: 'left' },
                timeShaft: 14,
                myMsg: JSON.parse(window.localStorage.getItem('userMsg')),
                curType: 'date',
                curSelectUser: null,
                curSelectUsername: null,
                // 当前选中的日期
                curDateTime: moment(new Date((new Date().getTime()))).format('YYYY-MM-DD'),
                // 快捷组件按钮的禁用情况 time(时间上限) / all / top / bottom / true
                top: true,
                bottom: false,
                time: false,
                // 当前快捷用户的下标位置
                forbUserIndex: 0,
                loading: true,
                startDate: new Date(new Date(new Date().toLocaleDateString()).getTime()),
                endDate: new Date(new Date(new Date().toLocaleDateString()).getTime()),
                timeDelta: '',
                timeSplits: [],
                timeData: [],
                groups: []
            }
        },
        watch: {
            groupusers (oldVal) {
                if (oldVal.length === 0 || oldVal.length === 1) {
                    this.top = true
                    this.bottom = true
                }
                this.filterUserId(this.username).then(res => {
                    this.curSelectUser = res
                    this.selectedType('member', true)
                })
            },
            curgroupid () {
                // 如果用户组发生了变化开始
                this.curType = 'date'
                this.changeDate(moment(this.curDateTime).format('YYYY-MM-DD'))
            },
            curdate (oldVal) {
                this.curDateTime = oldVal
                this.changeDate(oldVal)
            },
            curSelectUser () {
                this.selectUserIndex()
            },
            refreshpage () {
                if (this.curType === 'date') {
                    this.changeDate()
                } else {
                    this.changeUser()
                }
            }
        },
        created () {
            this.loadGroup()
            this.splitTime()
        },
        methods: {
            // 快捷切换(上)
            topItem () {
                if (this.curType === 'date') {
                    this.curDateTime = moment(this.curDateTime).subtract(1, 'days').format('YYYY-MM-DD')
                    this.changeDate(this.curDateTime)
                }
                // member
                if (this.curType === 'member') {
                    this.selectUserIndex()
                    if (this.forbUserIndex === 0 || this.groupusers.length === 1) {
                        // 灰色
                        this.top = true
                    } else {
                        this.curSelectUsername = this.groupusers[this.forbUserIndex - 1].username
                        this.curSelectUser = this.groupusers[this.forbUserIndex - 1].id
                        this.changeUser(this.groupusers[this.forbUserIndex - 1].id)
                        this.top = false
                    }
                    this.bottom = false
                }
            },
            // 快捷切换(下)
            bottomItem () {
                if (this.curType === 'date') {
                    this.curDateTime = moment(this.curDateTime).add(1, 'days').format('YYYY-MM-DD')
                    this.changeDate(this.curDateTime)
                }
                // member
                if (this.curType === 'member') {
                    this.selectUserIndex()
                    if (this.forbUserIndex === this.groupusers.length - 1) {
                        // 灰色
                        this.bottom = true
                    } else {
                        this.curSelectUsername = this.groupusers[this.forbUserIndex + 1].username
                        this.curSelectUser = this.groupusers[this.forbUserIndex + 1].id
                        this.changeUser(this.groupusers[this.forbUserIndex + 1].id)
                        this.bottom = false
                    }
                    this.top = false
                }
            },
            // 日期改变
            changeDate (flat = true) {
                this.loadTime()
            },
            // 成员的改变
            changeUser () {
                this.userTime()
            },
            // 切换 日期或者人名
            selectedType (type, flat = false) {
                // 跟换焦点
                this.curType = type
                // 切换到了用户 找第一个默认用户的开发时间(七天)
                if (type === 'member') {
                    if (this.groupusers.length !== 0) {
                        if (flat) {
                            // 链接跳进来
                            this.changeUser(this.curSelectUser)
                        } else {
                            // 不是链接跳进来
                            this.curSelectUser = this.groupusers[0].id
                            this.curSelectUsername = this.groupusers[0].username
                            this.changeUser(this.curSelectUser)
                        }
                    } else {
                        // 没成员就空
                        this.curSelectUser = ''
                        this.curSelectUsername = ''
                    }
                } else {
                    // 找当前时间的开发时间
                    this.changeDate(this.curDateTime, false)
                }
            },
            // 当前用户在数组的哪个地方
            selectUserIndex () {
                this.groupusers.forEach((item, index) => {
                    if (item.id === this.curSelectUser) {
                        this.forbUserIndex = index
                        if (index === 0 && index !== this.groupusers.length - 1) {
                            this.top = true
                            this.bottom = false
                        }
                        if (index !== 0 && index === this.groupusers.length - 1) {
                            this.top = false
                            this.bottom = true
                        }
                        if (index !== 0 && index !== this.groupusers.length - 1) {
                            this.top = false
                            this.bottom = false
                        }
                    }
                })
            },
            // 根据用户名过滤出用户id
            filterUserId (username) {
                return new Promise((resolve, reject) => {
                    this.groupusers.forEach(item => {
                        if (item.username === username) {
                            resolve(item.id)
                        }
                    })
                })
            },
            loadGroup () {
                this.$http.get(
                    '/list_admin_group/'
                ).then(res => {
                    if (res.result) {
                        this.groups = res.data

                        if (this.groups.length > 0) {
                            this.curgroupid = this.groups[0].id
                        }
                    }
                }).finally(() => {
                    this.loadTime()
                })
            },
            userTime () {
                if (!this.curSelectUser) {
                    return
                }
                this.loading = true
                this.$http.get(
                    '/user_free_time/?username=' + this.curSelectUsername
                ).then(res => {
                    if (res.result) {
                        this.timeData = res.data
                    } else {
                        this.$bkMessage({
                            theme: 'warning',
                            message: res.message
                        })
                    }
                }).finally(() => {
                    setTimeout(() => {
                        this.loading = false
                    }, 600)
                })
            },
            loadTime () {
                if (!this.curgroupid) {
                    return
                }
                this.loading = true
                const startDate = moment(this.curDateTime).format(moment.HTML5_FMT.DATE)
                const endDate = moment(this.curDateTime).format(moment.HTML5_FMT.DATE)
                if (this.curgroupid != null) {
                    this.loading = false
                    return
                }
                this.$http.get(
                    '/group_free_time/' + this.curgroupid + '/?start_date=' + startDate + '&end_date=' + endDate
                ).then(res => {
                    if (res.result) {
                        this.timeData = res.data
                    } else {
                        this.$bkMessage({
                            theme: 'warning',
                            message: res.message
                        })
                    }
                }).finally(() => {
                    setTimeout(() => {
                        this.loading = false
                    }, 600)
                })
            },
            splitTime () {
                this.timeSplits = []
                const delta = 1800000
                let i = 16
                while (this.startDate - (-(i + 1) * delta) <= this.endDate - (-24 * 3600 * 1000)) {
                    this.timeSplits.push({
                        startTime: new Date(this.startDate - (-i * delta)),
                        endTime: new Date(this.startDate - (-(i + 1) * delta))
                    })
                    i++
                    if (i === 44) {
                        break
                    }
                }
            },
            checkFreeTime (freeTime, timeDelta) {
                for (const i in freeTime) {
                    const startTime = new Date(freeTime[i].start_time)
                    const endTime = new Date(freeTime[i].end_time)
                    if ((moment(timeDelta.startTime).format('HH-mm-ss') >= moment(startTime).format('HH-mm-ss'))
                        && (moment(timeDelta.endTime).format('HH-mm-ss') <= moment(endTime).format('HH-mm-ss'))) {
                        return 'blue-background'
                    }
                }
                return 'gray-background'
            }
        }
    }
</script>
<style src='./index.css' scoped></style>
