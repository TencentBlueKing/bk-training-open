<template>
    <div @click="changeState" :class="state === true ? 'privacy' : 'open'">
        <bk-icon style="marginRight:3px" :type="state === true ? 'eye-slash' : 'eye' " />
        <div>{{scope === true ? '全部' : ''}}{{state === true ? '私密' : '公开'}}</div>
    </div>
</template>

<script>
    export default {
        props: {
            state: {
                type: Boolean,
                default: true
            },
            scope: {
                type: Boolean,
                default: false
            }
        },
        methods: {
            changeState () {
                this.state = !this.state
                this.$emit('changeState', this.state)
            }
        }
    }
</script>

<style scoped>
.open {
    font-size: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    padding:0 10px;
    justify-content: center;
    background: white;
    color: #63656e;
    border: 1px solid #c4c6cc;
}

.privacy {
    border: 1px solid #c4c6cc;
    color: #63656e;
     font-size: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    padding:0 10px;
    justify-content: center;
    background: white;
}

</style>
