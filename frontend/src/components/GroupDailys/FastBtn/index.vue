<template>
    <div class="fast-btn">
        <bk-button ext-cls="fast-btn-top" @click="topItem" :disabled="top">
            <bk-icon type="angle-up" />
        </bk-button>
        <bk-button ext-cls="fast-btn-bottom" @click="bottomItem" :disabled="bottom || time">
            <bk-icon type="angle-down" />
        </bk-button>
    </div>
</template>

<script>
    export default {
        props: {
            time: {
                type: Boolean
            },
            top: {
                type: Boolean
            },
            bottom: {
                type: Boolean
            }
        },
        methods: {
            topItem () {
                this.$emit('topItem')
            },
            bottomItem () {
                this.$emit('bottomItem')
            }
        }
    }
</script>

<style scoped>
.fast-btn {
  margin-left: 10px;
  height: 32px;
  display: flex;
  flex-direction: column;
}

.fast-btn-top,
.fast-btn-bottom {
  border: 1px solid #c4c6cc;
  display: flex;
  justify-content: center;
  align-items: center;
  flex: 1;
    overflow: hidden;
  height: 16px;
  min-width: 10px;
}

</style>
