<template>
    <div class="tabbtn">
        <span @click="selectBtn('first')" :class="active === 'first' ? 'Active' : 'noActive'">{{content[0]}}</span>
        <span>/</span>
        <span @click="selectBtn('second')" :class="active === 'second' ? 'Active' : 'noActive'">{{content[1]}}</span>
    </div>
</template>

<script>
    export default {
        props: {
            content: {
                type: Array
            },
            active: {
                type: String,
                default: 'first'
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
    font-size: 18px;
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
