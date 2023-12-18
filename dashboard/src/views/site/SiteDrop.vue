<template>
	<div class="shrink-0">
		<slot v-bind="{ showDialog }"></slot>
		<Dialog
			:options="{
				title: 'Xóa trang web',
				actions: [
					{
						label: site.archive_failed ? 'Ép buộc xóa' : 'Xóa',
						variant: 'solid',
						theme: 'red',
						loading: $resources.dropSite.loading,
						onClick: () => $resources.dropSite.submit()
					}
				]
			}"
			v-model="dialogOpen"
		>
			<template v-slot:body-content>
				<p class="text-base">
					Bạn có chắc chắn muốn xóa trang web không? Trang web sẽ được lưu trữ
					và tất cả các tệp tin và bản sao lưu ngoại vi sẽ bị xóa. Hành động này
					không thể được hoàn tác.
				</p>
				<p class="mt-4 text-base">
					Vui lòng nhập
					<span class="font-semibold">{{ site.name }}</span> để xác nhận.
				</p>
				<FormControl class="mt-4 w-full" v-model="confirmSiteName" />
				<div class="mt-4">
					<FormControl
						v-show="!site.archive_failed"
						id="auto-update-checkbox"
						v-model="forceDrop"
						type="checkbox"
						label="Force"
					/>
				</div>
				<ErrorMessage class="mt-2" :message="$resources.dropSite.error" />
			</template>
		</Dialog>
	</div>
</template>

<script>
export default {
	name: 'SiteDrop',
	props: ['site'],
	data() {
		return {
			dialogOpen: false,
			confirmSiteName: null,
			forceDrop: false
		};
	},
	resources: {
		dropSite() {
			return {
				url: 'press.api.site.archive',
				params: {
					name: this.site?.name,
					force: this.site.archive_failed == true ? true : this.forceDrop
				},
				onSuccess() {
					this.dialogOpen = false;
					this.$router.push('/sites');
				},
				validate() {
					if (this.site?.name !== this.confirmSiteName) {
						return 'Vui lòng nhập tên trang web để xác nhận';
					}
				}
			};
		}
	},
	methods: {
		showDialog() {
			this.dialogOpen = true;
		}
	}
};
</script>
