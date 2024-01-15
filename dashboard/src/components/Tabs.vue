<template>
	<div>
		<div>
			<ul class="hidden border-b text-base sm:flex">
				<router-link
					v-for="tab in tabs"
					:key="tab.label"
					:to="tab.route"
					v-slot="{ href, navigate, isActive }"
				>
					<li>
						<a
							class="font-base relative mr-4 block truncate border-b py-2 leading-none focus:outline-none"
							:class="[
								isTabSelected(tab)
									? 'border-brand border-gray-900 text-gray-900'
									: 'border-transparent text-gray-600 hover:text-gray-900'
							]"
							:href="href"
							@click="navigate"
						>
							<span>
								{{ tab.label }}
							</span>
							<div
								class="absolute right-0 top-1 h-1.5 w-1.5 rounded-full bg-red-500"
								v-if="tab.showRedDot && !isActive"
							></div>
						</a>
					</li>
				</router-link>
			</ul>
			<select
				class="form-select block w-full sm:hidden"
				@change="e => changeTab(e.target.value)"
			>
				<option
					v-for="tab in tabs"
					:selected="isTabSelected(tab)"
					:value="tab.route"
					:key="tab.label"
				>
					{{ tab.label }}
				</option>
			</select>
		</div>
		<div class="w-full pt-5" v-if="$slots.default">
			<Alert class="pb-2" title="" v-if="statusSite == 'Pending'">
				<span> Đang tiến hành khởi tạo hệ thống, quý khách vui lòng chờ. </span>
			</Alert>
			<slot></slot>
		</div>
	</div>
</template>

<script>
export default {
	name: 'Tabs',
	props: ['tabs', 'statusSite'],
	methods: {
		changeTab(route) {
			this.$router.replace(route);
		},
		isTabSelected(tab) {
			let route_path = decodeURIComponent(this.$route.path);
			return route_path.startsWith(tab.route);
		}
	}
};
</script>
