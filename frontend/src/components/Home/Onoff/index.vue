<template>
    <bk-button :hover-theme="scope ? 'primary' : ''" @click="changeState">
        <bk-icon style="marginRight:3px;" :type="state === true ? 'eye-slash' : 'eye' " />
        {{scope === true ? '全部' : ''}}{{state === true ? '私密' : '公开'}}
    </bk-button>
</template>

<script>
    import { bkButton } from 'bk-magic-vue'
    export default {
        components: {
            bkButton
        },
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
 .bk-button, .bk-default.active,   .bk-button.bk-default:active{
    border-color: none;
    color: #63656e;
}
</style>
