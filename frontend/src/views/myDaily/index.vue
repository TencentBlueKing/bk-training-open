<template>
    <div id="myDaily">
        <div>
            <bk-container>
                <bk-row>
                    <bk-col :span="5"><div class="content">
                        <!-- 选择日报模板 -->
                        <bk-select :disabled="false" v-model="value" class="mr15" style="width: 250px; display: inline-block;"
                            ext-cls="select-custom"
                            ext-popover-cls="select-popover-custom"
                            searchable
                            @change="handleSelectChange">
                            <bk-option v-for="option in templateList"
                                :key="option.id"
                                :id="option.id"
                                :name="option.name"
                            >
                            </bk-option>
                        </bk-select>
                    </div></bk-col>
                    <bk-col :span="5"><div class="content">
                        <!-- 选择日报日期 -->
                        <bk-date-picker class="mr15" v-model="reportDate"
                            :clearable="false"
                            :placeholder="'选择日期'"
                            :ext-popover-cls="'custom-popover-cls'"
                            :options="customOption"
                        >
                        </bk-date-picker>
                    </div></bk-col>
                    <bk-col :span="2"><div class="content">
                        <!-- 保存日报并且发送邮件 -->
                        <bk-button :theme="'default'" type="submit" :title="'保存'" @click="handleClick" class="mr10">
                            保存
                        </bk-button>
                    </div></bk-col>
                    <bk-col :span="2"><div class="content">
                        <!-- 保存状态标签 -->
                        <span class="tag-view">
                            <bk-tag id="saveTag" :theme="tagTheme">未保存</bk-tag>
                        </span>
                    </div></bk-col>
                </bk-row>
            </bk-container>
        </div>

        <!-- 写日报模块 -->
        <div v-for="(reportItem,index) of selectContent" :key="reportItem">
            {{reportItem}}
            <div class="input-demo">
                <bk-input
                    placeholder=""
                    :type="'textarea'"
                    :rows="3"
                    :maxlength="255"
                    v-model="reportContent[index]">
                </bk-input>
            </div>
        </div>
    </div>
</template>

<script>
    import { bkContainer, bkCol, bkRow, bkTag, bkOption, bkSelect } from 'bk-magic-vue'

    export default {
        components: {
            bkContainer,
            bkCol,
            bkRow,
            bkTag,
            bkSelect,
            bkOption
        },
        data (s) {
            return {
                value: '',
                templateList: [],
                selectID: null,
                selectContent: '',
                reportContent: [],
                reportDate: new Date(),
                tagTheme: 'info',
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
            this.$http.get('/get_all_report_template/').then(res => {
                if (res.result) {
                    this.templateList = res.data
                } else {
                    const config = {}
                    config.message = res.message
                    config.offsetY = 80
                    config.theme = 'error'
                    this.$bkMessage(config)
                }
            })
        },
        methods: {
            handleSelectChange (event) {
                this.selectID = event
                for (const template of this.templateList) {
                    if (template.id === this.selectID) {
                        this.selectContent = template.content.split(';')
                        break
                    }
                }
            },
            handleClick (event) {
                // 消息提示框的参数设置
                const config = {
                    'offsetY': 80
                }
                // 读取各个文本框的值
                const reportText = {}
                const len = this.reportContent.length
                if (len === 0) {
                    config.message = '请填写日报'
                    config.theme = 'error'
                    this.$bkMessage(config)
                    return
                }
                for (let i = 0; i < len; i++) {
                    console.log(this.reportContent[i])
                    if (this.reportContent[i].length === 0) {
                        config.message = '请填写日报'
                        config.theme = 'error'
                        this.$bkMessage(config)
                        return
                    }
                    reportText[this.selectContent[i]] = this.reportContent[i]
                }
                const year = this.reportDate.getFullYear()
                const month = this.reportDate.getMonth() + 1
                const date = this.reportDate.getDate()
                // 读取日期
                const data = {
                    'date': year + '-' + month + '-' + date,
                    'content': reportText
                }
                this.$http.post(`/daily_report/`, data).then(res => {
                    if (res.result) {
                        document.getElementById('saveTag').textContent = '已保存'
                        config.theme = 'success'
                    } else {
                        config.theme = 'error'
                    }
                    config.message = res.message
                    this.$bkMessage(config)
                })
            }
        }
    }
</script>

<style lang="postcss">

.wrapper {
    overflow: hidden;
    border: 1px solid #ddd;
    border-radius: 2px;
    padding: 20px 0;
}
.content {
    background-color: #e1ecff;
    height: 100%;
    line-height: 60px;
    border-radius: 2px;
    font-size: 12px;
}

.bk-grid-row {
    text-align: center;
}

.bk-grid-row + .bk-grid-row {
    margin-top: 30px;
}

.bk-grid-row + .bk-grid-row {
    margin-top: 10px;
}
</style>
