<template>
    <div :id="pageid" class="content-wapper">
        <div id="content" class="content">
            <slot></slot>
        </div>
    </div>
</template>

<script>
    export default {
        name: 'contentWapper',
        components: {},
        props: {
            pageid: {
                type: String,
                default: ''
            },
            minheight: {
                type: Number,
                default: 820
            }
        },
        data () {
            return {
               
            }
        },
        mounted () {
            this.setStyle()
        },
        methods: {
            setStyle () {
                document.querySelector('#content').style.minHeight = this.minheight + 'px'
                // console.log('document.querySelector(id).style.minHeight == ', document.querySelector(id).style)
            }
        }
    }
</script>

<style scoped>
.content-wapper{
    width: 100%;
    height: 100%;
    overflow-y: auto;
}
.content{
    border: 2px solid #EAEBF0 ;
    width: 90%;
    margin:0 auto;
    padding: 30px 50px 20px;
    max-width: 1710px;
}
</style>
