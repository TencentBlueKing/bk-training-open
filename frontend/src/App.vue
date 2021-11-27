<template>
    <div class="monitor-navigation">
        <bk-navigation
            :header-title="nav.id"
            :side-title="nav.title"
            :default-open="false"
            :navigation-type="curNav.nav"
            :need-menu="curNav.needMenu"
            @toggle="handleToggle"
        >
            <template slot="header">
                <div class="monitor-navigation-header">
                    <ol class="header-nav" v-if="curNav.nav === 'top-bottom'">
                        <bk-popover
                            v-for="(item, index) in header.list"
                            :key="item.id"
                            theme="light navigation-message"
                            :arrow="false"
                        >
                            <li
                                v-show="item.show"
                                class="header-nav-item"
                                style="margin-right:0px;margin-left:0px;text-decoration:none;"
                                @click="changeHead(index)"
                            >
                                <router-link :to="item.url" style="display:inline-block; width:90px; height:50px;line-height:50px;text-align:center;color:#979BA5;" :class="{ 'item-active': index === header.active }">   {{ item.name }}</router-link>
                            </li>
                        </bk-popover>
                    </ol>
                    <div v-else class="header-title">
                        <span class="header-title-icon">
                            <svg
                                class="icon"
                                style="
                  width: 1em;
                  height: 1em;
                  vertical-align: middle;
                  fill: currentColor;
                  overflow: hidden;
                "
                                viewBox="0 0 1024 1024"
                                version="1.1"
                                xmlns="http://www.w3.org/2000/svg"
                                p-id="4756"
                            >
                                <path
                                    d="M416 480h320v64H416l96 96-48 48-176-176 176-176 48 48-96 96z"
                                    p-id="4757"
                                ></path>
                            </svg>
                        </span>
                        {{ nav.id }}
                    </div>
                </div>
            </template>
            <div class="monitor-navigation-content">
                <router-view :key="routerKey" v-show="!mainContentLoading" />
            </div>
            <template slot="footer">
                <div class="monitor-navigation-footer">
                    Copyright © 2012-{{ new Date().getFullYear() }} Tencent BlueKing. All
                    Rights Reserved. 腾讯蓝鲸 版权所有
                </div>
            </template>
        </bk-navigation>
    </div>
</template>

<script>
    import {
        bkNavigation,
        bkPopover
    } from 'bk-magic-vue'
    export default {
        name: 'monitor-navigation',
        components: {
            bkNavigation,
            bkPopover
        },
        data () {
            return {
                navActive: 0,
                routerKey: +new Date(),
                navMap: [
                    {
                        nav: 'top-bottom',
                        needMenu: false,
                        name: '上下结构导航'
                    }
                ],
                nav: {
                    id: '首页一',
                    toggle: false,
                    submenuActive: false,
                    title: '蓝鲸日报平台'
                },
                header: {
                    list: [
                        {
                            name: '填写日报',
                            id: 1,
                            url: 'Home',
                            show: true
                        },
                        {
                            name: '日报查看',
                            id: 2,
                            url: 'groupDailys',
                            show: true
                        },
                        {
                            name: '我的小组',
                            id: 3,
                            url: 'myGroup',
                            show: true
                        },
                        {
                            name: '管理组',
                            id: 4,
                            url: 'manageGroup',
                            show: true
                        }
                    ],
                    active: 0,
                    bizId: 1
                }
            }
        },
        computed: {
            curNav () {
                return this.navMap[this.navActive]
            },
            curHeaderNav () {
                return this.header.list[this.header.active] || {}
            }
        },
        created () {
            // TODO=>判断是否为管理员
            // this.$http.get('/judge_admin/', { params: { username: this.$store.state.user.username } }).then(res => {
            //     if (!res.result) {
            //         this.header.list[3].show = false
            //     }
            // })
        },
        methods: {
            changeHead (index) {
                console.log('当前点击', index)
                const vm = this
                vm.header.active = index
            },
            handleSelect (id, item) {
                this.nav.id = id
                console.info(`你选择了${id}`)
            },
            handleToggle (v) {
                this.nav.toggle = v
            },
            beforeNavChange (newId, oldId) {
                console.info(newId, oldId)
                return true
            }
        }
    }
</script>

<style>
/* 以下样式是为了适应例子父级的宽高而设置 */
body{
    height:100%;
}
.bk-navigation {
  width: 100%;
  height: 100%;
  outline: 1px solid #ebebeb;
}
.header-nav-item a {
  text-decoration: none ;
}
.container-content{
    padding:0px!important;
}
.bk-navigation .bk-navigation-wrapper {
  height: calc(100vh - 252px) !important;
}
.bk-select >>> .bk-select-name{
  display:none;
}
.bk-navigation >>>.bk-icon{
  display:none;
}
/* 以上样式是为了适应例子父级的宽高而设置 */

.monitor-navigation-header {
  -webkit-box-flex: 1;
  -ms-flex: 1;
  flex: 1;
  height: 100%;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  font-size: 14px;
  width: 100%;
  height: 100%;
}
.monitor-navigation-header .header-nav {
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  padding: 0;
  margin: 0;
}
.monitor-navigation-header .header-nav-item {
  list-style: none;
  height: 50px;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  margin-right: 40px;
  color: #96a2b9;
  min-width: 56px;
}
.monitor-navigation-header .header-nav-item .item-active  {
  color: #ffffff !important;
}
.monitor-navigation-header .header-nav-item:hover {
  cursor: pointer;
  color: #d3d9e4;
}
.monitor-navigation-header .header-title {
  color: #63656e;
  font-size: 16px;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  margin-left: -6px;
}
.monitor-navigation-header .header-title-icon {
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  width: 28px;
  height: 28px;
  font-size: 28px;
  color: #3a84ff;
  cursor: pointer;
}
.monitor-navigation-header .header-select {
  width: 240px;
  margin-left: auto;
  margin-right: 34px;
  border: none;
  background: #252f43;
  color: #d3d9e4;
  -webkit-box-shadow: none;
  box-shadow: none;
}
.monitor-navigation-header .header-select.is-left {
  background: #f0f1f5;
  color: #63656e;
}
.monitor-navigation-header .header-mind {
  color: #768197;
  font-size: 16px;
  position: relative;
  height: 32px;
  width: 32px;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  -webkit-box-pack: center;
  -ms-flex-pack: center;
  justify-content: center;
  margin-right: 8px;
}
.monitor-navigation-header .header-mind.is-left {
  color: #63656e;
}
.monitor-navigation-header .header-mind.is-left:hover {
  color: #3a84ff;
  background: #f0f1f5;
}
.monitor-navigation-header .header-mind-mark {
  position: absolute;
  right: 8px;
  top: 8px;
  height: 7px;
  width: 7px;
  border: 1px solid #27334c;
  background-color: #ea3636;
  border-radius: 100%;
}
.monitor-navigation-header .header-mind-mark.is-left {
  border-color: #f0f1f5;
}
.monitor-navigation-header .header-mind:hover {
  background: -webkit-gradient(
    linear,
    right top,
    left top,
    from(rgba(37, 48, 71, 1)),
    to(rgba(38, 50, 71, 1))
  );
  background: linear-gradient(
    270deg,
    rgba(37, 48, 71, 1) 0%,
    rgba(38, 50, 71, 1) 100%
  );
  border-radius: 100%;
  cursor: pointer;
  color: #d3d9e4;
}
.monitor-navigation-header .header-help {
  color: #768197;
  font-size: 16px;
  position: relative;
  height: 32px;
  width: 32px;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  -webkit-box-pack: center;
  -ms-flex-pack: center;
  justify-content: center;
  margin-right: 8px;
}
.monitor-navigation-header .header-help.is-left {
  color: #63656e;
}
.monitor-navigation-header .header-help.is-left:hover {
  color: #3a84ff;
  background: #f0f1f5;
}
.monitor-navigation-header .header-help:hover {
  background: -webkit-gradient(
    linear,
    right top,
    left top,
    from(rgba(37, 48, 71, 1)),
    to(rgba(38, 50, 71, 1))
  );
  background: linear-gradient(
    270deg,
    rgba(37, 48, 71, 1) 0%,
    rgba(38, 50, 71, 1) 100%
  );
  border-radius: 100%;
  cursor: pointer;
  color: #d3d9e4;
}
.monitor-navigation-header .header-user {
  height: 100%;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  -webkit-box-pack: center;
  -ms-flex-pack: center;
  justify-content: center;
  color: #96a2b9;
  margin-left: 8px;
}
.monitor-navigation-header .header-user .bk-icon {
  margin-left: 5px;
  font-size: 12px;
}
.monitor-navigation-header .header-user.is-left {
  color: #63656e;
}
.monitor-navigation-header .header-user.is-left:hover {
  color: #3a84ff;
}
.monitor-navigation-header .header-user:hover {
  cursor: pointer;
  color: #d3d9e4;
}
.monitor-navigation-content {
  height: calc(100% - 84px);
  overflow-y: auto;
  background: #ffffff;
  -webkit-box-shadow: 0px 2px 4px 0px rgba(25, 25, 41, 0.05);
  box-shadow: 0px 2px 4px 0px rgba(25, 25, 41, 0.05);
  border-radius: 2px;
  border: 1px solid rgba(220, 222, 229, 1);
}
.monitor-navigation-footer {
  height: 52px;
  width: 100%;
  margin: 32px 0 0;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  -webkit-box-pack: center;
  -ms-flex-pack: center;
  justify-content: center;
  border-top: 1px solid #dcdee5;
  color: #63656e;
  font-size: 12px;
}
.monitor-navigation-message {
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-orient: vertical;
  -webkit-box-direction: normal;
  -ms-flex-direction: column;
  flex-direction: column;
  width: 360px;
  background-color: #ffffff;
  border: 1px solid #e2e2e2;
  border-radius: 2px;
  -webkit-box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
  box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
  color: #979ba5;
  font-size: 12px;
}
.monitor-navigation-message .message-title {
  -webkit-box-flex: 0;
  -ms-flex: 0 0 48px;
  flex: 0 0 48px;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  color: #313238;
  font-size: 14px;
  padding: 0 20px;
  margin: 0;
  border-bottom: 1px solid #f0f1f5;
}
.monitor-navigation-message .message-list {
  -webkit-box-flex: 1;
  -ms-flex: 1;
  flex: 1;
  max-height: 450px;
  overflow: auto;
  margin: 0;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-orient: vertical;
  -webkit-box-direction: normal;
  -ms-flex-direction: column;
  flex-direction: column;
  padding: 0;
}
.monitor-navigation-message .message-list-item {
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  width: 100%;
  padding: 0 20px;
}
.monitor-navigation-message .message-list-item .item-message {
  padding: 13px 0;
  line-height: 16px;
  min-height: 42px;
  -webkit-box-flex: 1;
  -ms-flex: 1;
  flex: 1;
  -ms-flex-wrap: wrap;
  flex-wrap: wrap;
  color: #63656e;
}
.monitor-navigation-message .message-list-item .item-date {
  padding: 13px 0;
  margin-left: 16px;
  color: #979ba5;
}
.monitor-navigation-message .message-list-item:hover {
  cursor: pointer;
  background: #f0f1f5;
}
.monitor-navigation-message .message-footer {
  -webkit-box-flex: 0;
  -ms-flex: 0 0 42px;
  flex: 0 0 42px;
  border-top: 1px solid #f0f1f5;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  -webkit-box-pack: center;
  -ms-flex-pack: center;
  justify-content: center;
  color: #3a84ff;
}
.monitor-navigation-nav {
  width: 150px;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-orient: vertical;
  -webkit-box-direction: normal;
  -ms-flex-direction: column;
  flex-direction: column;
  background: #ffffff;
  border: 1px solid #e2e2e2;
  -webkit-box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
  box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
  padding: 6px 0;
  margin: 0;
  color: #63656e;
}
.monitor-navigation-nav .nav-item {
  -webkit-box-flex: 0;
  -ms-flex: 0 0 32px;
  flex: 0 0 32px;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  padding: 0 20px;
  list-style: none;
}
.monitor-navigation-nav .nav-item:hover {
  color: #3a84ff;
  cursor: pointer;
  background-color: #f0f1f5;
}
.monitor-navigation-admin {
  width: 170px #63656e;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-orient: vertical;
  -webkit-box-direction: normal;
  -ms-flex-direction: column;
  flex-direction: column;
  background: #ffffff;
  border: 1px solid #e2e2e2;
  -webkit-box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
  box-shadow: 0px 3px 4px 0px rgba(64, 112, 203, 0.06);
  padding: 6px 0;
  margin: 0;
  color: #63656e;
}
.monitor-navigation-admin .nav-item {
  -webkit-box-flex: 0;
  -ms-flex: 0 0 32px;
  flex: 0 0 32px;
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
  padding: 0 20px;
  list-style: none;
}
.monitor-navigation-admin .nav-item:hover {
  color: #3a84ff;
  cursor: pointer;
  background-color: #f0f1f5;
}
.tippy-popper .tippy-tooltip.navigation-message-theme {
  padding: 0;
  border-radius: 0;
  -webkit-box-shadow: none;
  box-shadow: none;
}
</style>
