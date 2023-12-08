<template>
	<Card title="Bản phát hành ứng dụng">
		<div v-if="sources.length">
			<div class="flex flex-row items-baseline">
				<FormControl
					type="select"
					v-if="sources.length > 1"
					v-model="selectedSource"
					:options="
						sources.map(s => ({
							label: `${s.source_information.repository}:${s.source_information.branch}`,
							value: s.source
						}))
					"
				/>
			</div>
		</div>
		<div v-if="!sources.length">
			<p class="mt-3 text-center text-lg text-gray-600">
				Không có nguồn ứng dụng đã xuất bản cho ứng dụng này. Vui lòng liên hệ
				với bộ phận hỗ trợ để xuất bản một phiên bản của ứng dụng này.
			</p>
		</div>
		<div
			v-else-if="releasesList.length === 0 && !$resources.releases.list.loading"
		>
			<p class="mt-3 text-center text-lg text-gray-600">
				Không có phiên bản của ứng dụng đã được tạo ra cho phiên bản này.
			</p>
		</div>

		<div v-else>
			<div class="divide-y">
				<div
					class="grid grid-cols-3 items-center gap-x-8 py-4 text-base text-gray-600 md:grid-cols-6"
				>
					<span class="md:col-span-2">Tin nhắn xác nhận</span>
					<span class="hidden md:inline">Thẻ</span>
					<span class="hidden md:inline">Tác giả</span>
					<span>Trạng thái</span>
					<span></span>
				</div>

				<div
					v-for="release in releasesList"
					:key="release.name"
					class="grid grid-cols-3 items-center gap-x-8 py-4 text-base text-gray-900 md:grid-cols-6"
				>
					<p
						class="max-w-md truncate text-base font-medium text-gray-700 md:col-span-2"
					>
						{{ release.message }}
					</p>
					<CommitTag
						class="hidden md:flex"
						:tag="release.tag || release.hash.slice(0, 6)"
						:link="getCommitUrl(release.hash)"
					/>
					<span class="hidden text-gray-600 md:inline">
						{{ release.author }}
					</span>
					<span>
						<Badge v-if="release.status != 'Draft'" :label="release.status" />
					</span>
					<span class="text-right">
						<Button
							v-if="isPublishable(release)"
							:loading="
								$resources.createApprovalRequest.loading ||
								$resources.latestApproved.loading
							"
							@click="confirmApprovalRequest(release.name)"
						>
							Xuất bản
						</Button>

						<Button
							v-else-if="release.status == 'Awaiting Approval'"
							@click="confirmCancelRequest(release.name)"
							>Hủy</Button
						>

						<Button
							v-else-if="release.status == 'Rejected'"
							@click="showFeedback(release)"
							>Xem phản hồi</Button
						>
					</span>
				</div>
				<Dialog
					:options="{ title: 'Lý do từ chối' }"
					v-model="showRejectionFeedbackDialog"
				>
					<template v-slot:body-content>
						<div class="prose text-lg" v-html="rejectionFeedback"></div>
					</template>
				</Dialog>

				<div class="py-3">
					<Button
						@click="$resources.releases.next()"
						v-if="$resources.releases.hasNextPage"
						:loading="$resources.releases.list.loading"
						loadingText="Đang tải..."
						>Tải thêm</Button
					>
				</div>
			</div>
		</div>
	</Card>
</template>

<script>
import CommitTag from './utils/CommitTag.vue';
import { notify } from '@/utils/toast';

export default {
	props: {
		app: {
			type: Object
		}
	},
	data() {
		return {
			showRejectionFeedbackDialog: false,
			rejectionFeedback: '',
			selectedSource: null
		};
	},
	mounted() {
		this.$socket.on('new_app_release_created', this.releaseStateUpdate);
		this.$socket.on('request_status_changed', this.releaseStateUpdate);
		if (this.sources.length > 0) {
			this.selectedSource = this.sources[0].source;
		}
	},
	resources: {
		releases() {
			return {
				type: 'list',
				doctype: 'App Release',
				url: 'press.api.marketplace.releases',
				filters: {
					app: this.app.app,
					source: this.selectedSource
				},
				start: 0,
				pageLength: 15,
				auto: true
			};
		},
		appSource() {
			return {
				url: 'press.api.marketplace.get_app_source',
				params: {
					name: this.selectedSource
				}
			};
		},
		latestApproved() {
			return {
				url: 'press.api.marketplace.latest_approved_release',
				params: {
					source: this.selectedSource
				},
				auto: true
			};
		},
		createApprovalRequest() {
			return {
				url: 'press.api.marketplace.create_approval_request',
				onSuccess() {
					this.resetReleaseListState();
				},
				onError(err) {
					const requestAlreadyExists = err.messages.some(msg =>
						msg.includes('already awaiting approval')
					);

					if (requestAlreadyExists)
						notify({
							title: 'Yêu cầu đã tồn tại',
							message: err.messages.join('\n'),
							color: 'red',
							icon: 'x'
						});
					else
						notify({
							title: 'Lỗi',
							message: err.messages.join('\n'),
							color: 'red',
							icon: 'x'
						});
				}
			};
		},
		cancelApprovalRequest() {
			return {
				url: 'press.api.marketplace.cancel_approval_request',
				onSuccess() {
					this.resetReleaseListState();
				}
			};
		}
	},
	methods: {
		isPublishable(release) {
			return (
				release.status == 'Draft' &&
				(!this.latestApprovedOn ||
					this.$date(release.creation) > this.latestApprovedOn)
			);
		},
		createApprovalRequest(appRelease) {
			let { app } = this.app;
			this.$resources.createApprovalRequest.submit({
				marketplace_app: app,
				app_release: appRelease
			});
		},
		cancelApprovalRequest(appRelease) {
			let { app } = this.app;
			this.$resources.cancelApprovalRequest.submit({
				marketplace_app: app,
				app_release: appRelease
			});
		},
		resetReleaseListState() {
			this.$resources.releases.reload();
			this.$resources.latestApproved.reload();
		},
		showFeedback(appRelease) {
			this.showRejectionFeedbackDialog = true;
			this.rejectionFeedback = appRelease.reason_for_rejection;
		},
		confirmApprovalRequest(appRelease) {
			this.$confirm({
				title: 'Xuất bản phiên bản',
				message:
					'Bạn có chắc muốn xuất bản phiên bản này lên marketplace không? Khi xác nhận, phiên bản sẽ được gửi đi để được xác nhận bởi nhóm đánh giá.',
				actionLabel: 'Xuất bản',
				action: closeDialog => {
					closeDialog();
					this.createApprovalRequest(appRelease);
				}
			});
		},
		confirmCancelRequest(appRelease) {
			this.$confirm({
				title: 'Hủy yêu cầu phê duyệt phiên bản',
				message:
					'Bạn có chắc muốn <strong>hủy</strong> yêu cầu xuất bản cho phiên bản này không?',
				actionLabel: 'Tiếp tục',
				actionColor: 'red',
				action: closeDialog => {
					closeDialog();
					this.cancelApprovalRequest(appRelease);
				}
			});
		},
		getCommitUrl(releaseHash) {
			return this.repoUrl ? `${this.repoUrl}/commit/${releaseHash}` : '';
		},
		releaseStateUpdate(data) {
			if (this.selectedSource && data.source == this.selectedSource) {
				this.resetReleaseListState();
			}
		}
	},
	computed: {
		releasesList() {
			if (!this.$resources.releases.data) {
				return [];
			}
			return this.$resources.releases.data;
		},
		latestApprovedOn() {
			if (
				this.$resources.latestApproved.data &&
				!this.$resources.latestApproved.loading
			) {
				return this.$date(this.$resources.latestApproved.data.creation);
			}
		},
		sources() {
			// Return only the unique sources
			let tempArray = [];
			for (let source of this.app.sources) {
				if (!tempArray.find(x => x.source === source.source)) {
					tempArray.push(source);
				}
			}
			return tempArray;
		},
		repoUrl() {
			return this.$resources.appSource?.data?.repository_url;
		}
	},
	watch: {
		selectedSource(value) {
			if (value) {
				this.resetReleaseListState();
				this.$resources.appSource.submit({ name: value });
			}
		}
	},
	components: { CommitTag }
};
</script>
