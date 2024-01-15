<template>
	<Card
		title="Tên miền"
		:subtitle="
			domains.data && domains.data.length
				? 'Tên miền trỏ đến tổ chức của bạn'
				: 'Không có tên miền nào đang trỏ đến tổ chức của bạn'
		"
	>
		<template #actions>
			<Button
				@click="showDialog = true"
				:disabled="site.status === 'Suspended'"
			>
				Thêm tên miền
			</Button>
		</template>
		<div class="divide-y" v-if="domains.data">
			<div v-for="d in domains.data" :key="d.name">
				<div class="py-2">
					<div class="flex items-center">
						<div class="flex w-2/3 text-base font-medium">
							<a
								class="text-blue-500"
								:href="'https://' + d.domain"
								target="_blank"
								v-if="d.status === 'Active'"
							>
								{{ d.domain }}
							</a>
							<span v-else>{{ d.domain }}</span>
							<div
								class="flex"
								v-if="d.redirect_to_primary == 1 && d.status == 'Active'"
							>
								<FeatherIcon name="arrow-right" class="mx-1 w-4" />
								<a
									class="text-blue-500"
									:href="'https://' + d.domain"
									target="_blank"
									v-if="d.status === 'Active'"
								>
									{{ site.host_name }}
								</a>
							</div>
						</div>
						<div class="ml-auto flex items-center space-x-2">
							<Badge
								v-if="d.status == 'Active' && d.primary"
								:label="'Primary'"
							/>
							<Badge v-else-if="d.status != 'Active'" :label="d.status" />
							<Button
								v-if="d.status == 'Broken' && d.retry_count <= 5"
								:loading="$resources.retryAddDomain.loading"
								@click="
									$resources.retryAddDomain.submit({
										name: site.name,
										domain: d.domain
									})
								"
							>
								Thử lại
							</Button>
							<Button v-if="$resources.removeDomain.loading" :loading="true">
								Gỡ bỏ tên miền
							</Button>
							<Dropdown v-else :options="actionItems(d)">
								<template v-slot="{ open }">
									<Button icon="more-horizontal" />
								</template>
							</Dropdown>
						</div>
					</div>
					<ErrorMessage
						v-if="d.status == 'Broken'"
						error="Chúng tôi gặp sự cố khi thêm tên miền."
					/>
					<ErrorMessage :message="$resources.removeDomain.error" />
					<ErrorMessage :message="$resources.setHostName.error" />
				</div>
			</div>
		</div>
		<Dialog v-model="showDialog" :options="{ title: 'Thêm tên miền' }">
			<template v-slot:body-content>
				<div class="space-y-4">
					<p class="text-base">
						Để thêm một tên miền tùy chỉnh, bạn phải đã sở hữu nó trước. Nếu bạn
						chưa có một, hãy mua và quay lại đây.
					</p>
					<FormControl
						placeholder="www.example.com"
						v-model="newDomain"
						:readonly="dnsVerified"
					/>

					<div v-if="newDomain && !dnsVerified" class="space-y-2 text-base">
						<p>Tạo một trong các bản ghi DNS sau đây</p>
						<p class="px-2">
							<span class="font-semibold text-gray-700">CNAME</span> bản ghi từ
							<span class="font-semibold text-gray-700">{{ newDomain }}</span>
							đến
							<span class="font-semibold text-gray-700">{{ site.name }}</span>
						</p>
						<p class="px-2">
							<span class="font-semibold text-gray-700">A</span> bản ghi từ
							<span class="font-semibold text-gray-700">{{ newDomain }}</span>
							đến
							<span class="font-semibold text-gray-700">{{ site.ip }}</span>
						</p>
					</div>
					<div v-if="dnsResult && !dnsResult.matched" class="space-y-2">
						<p class="text-base">
							Nhận các phản hồi truy vấn DNS sau cho
							<span class="font-semibold text-gray-700">{{ newDomain }}</span
							>.
						</p>
						<div
							v-if="newDomain && dnsResult.CNAME && !dnsResult.CNAME.matched"
							class="space-y-2"
						>
							<p class="text-base">
								<span class="font-semibold text-gray-700">CNAME</span>
							</p>
							<div
								class="flex flex-row items-center justify-between rounded-lg border-2 p-2"
							>
								<p
									class="select-all overflow-hidden font-mono text-sm text-gray-800"
								>
									{{ dnsResult.CNAME.answer }}
								</p>
							</div>
						</div>
						<div
							v-if="newDomain && dnsResult.A && !dnsResult.A.matched"
							class="space-y-2"
						>
							<p class="text-base">
								<span class="font-semibold text-gray-700">A</span>
							</p>
							<div
								class="flex flex-row items-center justify-between rounded-lg border-2 p-2"
							>
								<p
									class="select-all overflow-hidden font-mono text-sm text-gray-800"
								>
									{{ dnsResult.A.answer }}
								</p>
							</div>
						</div>
					</div>
					<p class="flex text-base" v-if="dnsVerified === false">
						<FeatherIcon
							name="x"
							class="mr-2 h-5 w-5 rounded-full bg-red-100 p-1 text-red-500"
						/>
						Xác minh DNS thất bại
					</p>
					<p class="flex text-base" v-if="dnsVerified === true">
						<FeatherIcon
							name="check"
							class="mr-2 h-5 w-5 rounded-full bg-green-100 p-1 text-green-500"
						/>
						Bản ghi DNS đã được xác minh thành công. Nhấp vào 'Thêm tên miền'.
					</p>
					<ErrorMessage :message="$resources.checkDNS.error" />
					<ErrorMessage :message="$resources.addDomain.error" />
					<ErrorMessage :message="$resources.retryAddDomain.error" />
				</div>
			</template>

			<template #actions>
				<Button
					v-if="!dnsVerified"
					class="mt-2 w-full"
					variant="solid"
					:loading="$resources.checkDNS.loading"
					@click="
						$resources.checkDNS.submit({
							name: site.name,
							domain: newDomain
						})
					"
				>
					Xác minh DNS
				</Button>
				<Button
					v-if="dnsVerified"
					class="mt-2 w-full"
					variant="solid"
					:loading="$resources.addDomain.loading"
					@click="
						$resources.addDomain.submit({
							name: site.name,
							domain: newDomain
						})
					"
				>
					Thêm tên miền
				</Button>
			</template>
		</Dialog>
	</Card>
</template>

<script>
import { notify } from '@/utils/toast';

export default {
	name: 'SiteOverviewDomains',
	props: ['site'],
	data() {
		return {
			showDialog: false,
			newDomain: null
		};
	},
	resources: {
		domains() {
			return {
				url: 'press.api.site.domains',
				params: { name: this.site?.name },
				auto: true
			};
		},
		checkDNS: {
			url: 'press.api.site.check_dns',
			validate() {
				if (!this.newDomain) return 'Tên miền không thể để trống';
			}
		},
		addDomain: {
			url: 'press.api.site.add_domain',
			onSuccess() {
				this.$resources.checkDNS.reset();
				this.$resources.domains.reload();
				this.showDialog = false;
			}
		},
		removeDomain: {
			url: 'press.api.site.remove_domain',
			onSuccess() {
				this.$resources.domains.reload();
			}
		},
		retryAddDomain: {
			url: 'press.api.site.retry_add_domain',
			onSuccess() {
				this.$resources.domains.fetch();
			}
		},
		setHostName: {
			url: 'press.api.site.set_host_name',
			onSuccess() {
				this.$resources.domains.reload();
			}
		},
		setupRedirect: {
			url: 'press.api.site.set_redirect',
			onSuccess() {
				this.$resources.domains.reload();
			}
		},
		removeRedirect: {
			url: 'press.api.site.unset_redirect',
			onSuccess() {
				this.$resources.domains.reload();
			}
		}
	},
	computed: {
		domains() {
			return this.$resources.domains;
		},
		dnsVerified() {
			return this.dnsResult?.matched;
		},
		dnsResult() {
			return this.$resources.checkDNS.data;
		},
		primaryDomain() {
			return this.$resources.domains.data.filter(d => d.primary)[0].domain;
		}
	},
	watch: {
		newDomain() {
			this.$resources.checkDNS.reset();
		}
	},
	methods: {
		actionItems(domain) {
			return [
				{
					label: 'Xóa',
					onClick: () => this.confirmRemoveDomain(domain.domain)
				},
				{
					label: 'Đặt làm chính',
					condition: () => domain.status == 'Active' && !domain.primary,
					onClick: () => this.confirmSetPrimary(domain.domain)
				},
				{
					label: 'Chuyển hướng đến Chính',
					condition: () =>
						domain.status == 'Active' &&
						!domain.primary &&
						!domain.redirect_to_primary,
					onClick: () => this.confirmSetupRedirect(domain.domain)
				},
				{
					label: 'Xóa chuyển hướng',
					condition: () =>
						domain.status == 'Active' &&
						!domain.primary &&
						domain.redirect_to_primary,
					onClick: () => this.confirmRemoveRedirect(domain.domain)
				}
			].filter(d => (d.condition ? d.condition() : true));
		},
		confirmRemoveDomain(domain) {
			this.$confirm({
				title: 'Gỡ bỏ tên miền',
				message: `Bạn có chắc chắn muốn gỡ bỏ tên miền <b>${domain}</b>?`,
				actionLabel: 'Gỡ',
				actionColor: 'red',
				action: closeDialog => {
					closeDialog();
					this.$resources.removeDomain.submit({
						name: this.site.name,
						domain: domain
					});
				}
			});
		},
		confirmSetPrimary(domain) {
			let workingRedirects = false;
			this.$resources.domains.data.forEach(d => {
				if (d.redirect_to_primary) {
					workingRedirects = true;
				}
			});

			if (workingRedirects) {
				notify({
					title: 'Vui lòng gỡ bỏ tất cả các chuyển hướng đang hoạt động',
					color: 'red',
					icon: 'x'
				});
			} else {
				this.$confirm({
					title: 'Đặt làm tên miền chính',
					message: `Đặt làm chính sẽ làm cho <b>${domain}</b> trở thành URL chính cho tổ chức của bạn. Bạn có muốn tiếp tục không?`,
					actionLabel: 'Đặt làm chính',
					action: closeDialog => {
						closeDialog();
						this.$resources.setHostName.submit({
							name: this.site.name,
							domain: domain
						});
					}
				});
			}
		},
		confirmSetupRedirect(domain) {
			this.$confirm({
				title: 'Chuyển hướng đến tên miền chính',
				message: `Chuyển hướng đến Chính sẽ chuyển hướng <b>${domain}</b> đến <b>${this.primaryDomain}</b>. Bạn có muốn tiếp tục không?`,
				actionLabel: 'Chuyển hướng đến chính',
				action: closeDialog => {
					closeDialog();
					this.$resources.setupRedirect.submit({
						name: this.site.name,
						domain: domain
					});
				}
			});
		},
		confirmRemoveRedirect(domain) {
			this.$confirm({
				title: 'Xóa chuyển hướng',
				message: `Xóa chuyển hướng sẽ gỡ bỏ chuyển hướng đã thiết lập trước đó từ <b>${domain}</b> đến <b>${this.primaryDomain}</b>. Bạn có muốn tiếp tục không?`,
				actionLabel: 'Xóa chuyển hướng',
				action: closeDialog => {
					closeDialog();
					this.$resources.removeRedirect.submit({
						name: this.site.name,
						domain: domain
					});
				}
			});
		}
	}
};
</script>
