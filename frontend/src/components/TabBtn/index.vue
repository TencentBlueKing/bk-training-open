<template>
    <div class="tabbtn">
        <span @click="selectBtn(1)" :class="active === 1 ? 'Active' : 'noActive'">{{content[0]}}</span>
        <span>/</span>
        <span @click="selectBtn(2)" :class="active === 2 ? 'Active' : 'noActive'">{{content[1]}}</span>
    </div>
</template>

<script>
    export default {
        props: {
            content: {
                type: Array
            },
            active: {
                type: Number,
                default: 1
            }
        },
        methods: {
            selectBtn (val) {
                this.active = val
                this.$emit('changeType', val)
            }
        }
    }
</script>

<style scoped>
.tabbtn {
    display: flex;
    align-items: center;
}

.tabbtn span {
    font-size: 14px;
    flex-shrink: 0;
    padding-right: 10px;
}

.Active,.noActive {
    cursor: pointer;
}

.Active {
    color: #7384ff;
}
</style>
