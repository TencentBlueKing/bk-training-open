<template>
    <div class="groupDailys">
        <div class="groupDailys-btn">
            <div><bk-select
                :disabled="false"
                v-model="selectGroup"
                @selected="changeGroup"
                style="width: 250px;"
                ext-cls="selectgroup"
                :clearable="false"
                behavior="simplicity"
                searchable>
                <bk-option v-for="option in groupList"
                    :key="option.id"
                    :id="option.id"
                    :name="option.name">
                </bk-option>
            </bk-select></div>
            <!-- 小组日报 / 优秀日报 -->
            <TabBtn @changeType="changeType" :content="tabBtncontent" :active="active"></TabBtn>
        </div>
        <!-- 分割线 -->
        <div class="group-dailys-rule"></div>
        <keep-alive>
            <component :is="curComponents"></component>
        </keep-alive>
    </div>
</template>

<script>
    import { bkSelect, bkOption } from 'bk-magic-vue'
    import TabBtn from '@/components/TabBtn/index.vue'
    import GroupDaily from '@/components/GroupDailys/GroupDaily'
    import ExcellentDaily from '@/components/GroupDailys/ExcellentDaily'
    import requestApi from '@/api/request.js'
    const { getallGroups } = requestApi
    export default {
        components: {
            bkSelect,
            bkOption,
            TabBtn,
            GroupDaily,
            ExcellentDaily
        },
        data () {
            return {
                // 当前选中的组
                selectGroup: '',
                // 当前活着的组件
                curComponents: 'GroupDaily',
                tabBtncontent: ['小组日报', '优秀日报'],
                groupList: [],
                active: 'first'
            }
        },
        created () {
            getallGroups().then(res => {
                this.selectGroup = res.data[0].id
                this.groupList = res.data
                this.$store.commit('groupDaily/setGroupID', res.data[0].id)
                this.takeGroupuser()
            })
        },
        methods: {
            changeType (type) {
                this.active = type
                // 控制小组日报 还是 优秀日报
                this.curComponents = type === 'first' ? 'GroupDaily' : 'ExcellentDaily'
                this.$store.commit('groupDaily/setGroupID', this.selectGroup)
            },
            changeGroup (val) {
                this.selectGroup = val
                this.$store.commit('groupDaily/setGroupID', val)
            },
            // 跳转到的 组下的人
            takeGroupuser () {
                // 跳转过来的
                window.location.href.replace(/group=(.+)&username=(.+)/g, (_, $1, $2) => {
                    this.selectGroup = $1
                    // 外来链接的跳转
                    this.$store.commit('groupDaily/setGroupID', $1)
                    this.$store.commit('groupDaily/setselectUserId', $2)
                })
            }
        }

    }
</script>

<style >
    @import url('./index.css');
</style>
